package main

import (
	"bytes"
	"context"
	"encoding/base64"
	"encoding/json"
	"fmt"
	"image"
	"image/jpeg"
	"image/png"
	"io"
	"net/http"
	"os"
	"path/filepath"
	"strconv"
	"strings"
	"time"

	"eyes_remk/internal/config"
	ihandlers "eyes_remk/internal/handlers"
	"eyes_remk/internal/models"
	"eyes_remk/internal/services"
	"eyes_remk/pkg/database"
	"eyes_remk/pkg/logging"
	"eyes_remk/pkg/proxy"

	"github.com/gin-contrib/cors"
	"github.com/gin-gonic/gin"
	"gorm.io/gorm"
)

// HTTPServer HTTP服务器结构
type HTTPServer struct {
	server      *http.Server
	authService *services.AuthService
	database    *database.Database
	ctx         context.Context
	proxy       *proxy.ThirdPartyProxy // 添加第三方服务代理
}

// NewHTTPServer 创建HTTP服务器
func NewHTTPServer(ctx context.Context, authService *services.AuthService, database *database.Database, proxy *proxy.ThirdPartyProxy) *HTTPServer {
	return &HTTPServer{
		authService: authService,
		database:    database,
		ctx:         ctx,
		proxy:       proxy,
	}
}

// Start 启动HTTP服务器
func (h *HTTPServer) Start(port string) error {
	// 设置Gin模式
	gin.SetMode(gin.ReleaseMode)

	// 创建Gin引擎
	router := gin.New()

	// 添加中间件
	router.Use(gin.Logger())
	router.Use(gin.Recovery())

	// 配置CORS
	config := cors.DefaultConfig()
	config.AllowAllOrigins = true // 开发环境允许所有来源
	config.AllowMethods = []string{"GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"}
	config.AllowHeaders = []string{
		"Origin", "Content-Type", "Content-Length", "Accept-Encoding",
		"X-CSRF-Token", "Authorization", "accept", "origin", "Cache-Control",
		"X-Requested-With", "X-Request-ID",
	}
	config.AllowCredentials = true
	router.Use(cors.New(config))

	// 添加请求日志中间件
	router.Use(h.requestLoggerMiddleware())

	// 健康检查端点
	router.GET("/health", h.healthCheck)

	// API路由组
	api := router.Group("/api")
	{
		// 初始化新系统处理器与检查处理器（适配旧数据库类型）
		// 使用新架构的数据库
		systemHandlers := ihandlers.NewSystemHandlers(h.database)
		examHandlers := ihandlers.NewExaminationHandlers(h.database)
		patientHandlers := ihandlers.NewPatientHandlers(h.database)
		registrationHandlers := ihandlers.NewRegistrationHandlers(h.database)
		visitManagementHandlers := ihandlers.NewVisitManagementHandlers(h.database)
		imageHandlers := ihandlers.NewImageHandlers(h.database)
		diagnosisHandlers := ihandlers.NewDiagnosisHandlers(h.database)
		userHandlers := ihandlers.NewUserHandlers(h.database)
		roleHandlers := ihandlers.NewRoleHandlers(h.database)
		permissionHandlers := ihandlers.NewPermissionHandlers(h.database)
		configHandlers := ihandlers.NewConfigHandlers()

		// 认证相关路由
		auth := api.Group("/auth")
		{
			// 初始化认证处理器
			authHandlers := ihandlers.NewAuthHandlers(h.database, h.authService)
			auth.POST("/login", authHandlers.Login)
			auth.POST("/refresh", authHandlers.RefreshToken)
			auth.POST("/validate", authHandlers.ValidateToken)
			auth.POST("/logout", h.authMiddleware(), authHandlers.Logout)
			auth.GET("/user", h.authMiddleware(), authHandlers.GetCurrentUser)
			auth.POST("/change-password", h.authMiddleware(), authHandlers.ChangePassword)
		}

		// 系统相关路由
		system := api.Group("/system")
		system.Use(h.authMiddleware())
		{
			system.GET("/info", systemHandlers.GetSystemInfo)
			system.GET("/stats", systemHandlers.GetSystemStats)
			system.GET("/logs", systemHandlers.GetSystemLogs)
			system.DELETE("/logs", systemHandlers.ClearSystemLogs)
		}

		// 配置相关路由
		configs := api.Group("/configs")
		configs.Use(h.authMiddleware())
		{
			configs.GET("", configHandlers.GetConfigs)
			configs.GET("/database", configHandlers.GetDatabaseConfig)
			configs.PUT("/database", configHandlers.UpdateDatabaseConfig)
			configs.GET("/logging", configHandlers.GetLoggingConfig)
			configs.PUT("/logging", configHandlers.UpdateLoggingConfig)
			configs.GET("/other", configHandlers.GetOtherConfig)
			configs.PUT("/other", configHandlers.UpdateOtherConfig)
		}

		// 患者管理路由
		patients := api.Group("/patients")
		patients.Use(h.authMiddleware())
		{
			patients.GET("", patientHandlers.GetPatients)          // 切换到新实现
			patients.POST("", patientHandlers.CreatePatient)       // 切换到新实现
			patients.GET("/:id", patientHandlers.GetPatient)       // 切换到新实现
			patients.PUT("/:id", patientHandlers.UpdatePatient)    // 切换到新实现
			patients.DELETE("/:id", patientHandlers.DeletePatient) // 切换到新实现
		}

		// 挂号管理路由
		registrations := api.Group("/registrations")
		registrations.Use(h.authMiddleware())
		{
			registrations.GET("", registrationHandlers.GetRegistrations)           // 切换到新实现
			registrations.GET("/stats", registrationHandlers.GetRegistrationStats) // 切换到新实现
			registrations.POST("", registrationHandlers.CreateRegistration)        // 切换到新实现
			registrations.GET("/:id", registrationHandlers.GetRegistration)        // 切换到新实现
			registrations.PUT("/:id", registrationHandlers.UpdateRegistration)     // 切换到新实现
			registrations.DELETE("/:id", registrationHandlers.DeleteRegistration)  // 切换到新实现
			registrations.PATCH("/:id/status", h.updateRegistrationStatus)         // 暂时保持旧实现
		}

		// 就诊管理路由（联合查询registration和examination）
		visitManagement := api.Group("/visit-management")
		visitManagement.Use(h.authMiddleware())
		{
			visitManagement.GET("", visitManagementHandlers.GetVisitManagementList) // 切换到新实现
		}

		// 检查记录路由
		examinations := api.Group("/examinations")
		examinations.Use(h.authMiddleware())
		{
			// 仅将列表接口委托到新实现，其他保持旧实现，降低迁移风险
			examinations.GET("", examHandlers.GetExaminations)
			examinations.GET("/with-patients", examHandlers.GetPatientExaminations)
			examinations.GET("/stats", examHandlers.GetExaminationStats)
			examinations.GET("/types", examHandlers.GetExaminationTypes)
			examinations.GET("/types/:id", examHandlers.GetExaminationType)
			examinations.POST("", examHandlers.CreateExamination)
			examinations.GET("/:id", examHandlers.GetExamination)
			examinations.PUT("/:id", examHandlers.UpdateExamination)
			examinations.PATCH("/:id/status", examHandlers.UpdateExaminationStatus) // 更新检查状态
			examinations.DELETE("/:id", examHandlers.DeleteExamination)
		}

		// 图像管理路由
		images := api.Group("/images")
		images.Use(h.authMiddleware())
		{
			images.GET("", imageHandlers.GetFundusImages)                 // 切换到新实现
			images.POST("", imageHandlers.UploadFundusImage)              // 切换到新实现
			images.POST("/save-image", h.saveImageToLocalFunc)            // 暂时保持旧实现
			images.POST("/save-multi-image", h.saveMultiImageToLocalFunc) // 暂时保持旧实现
			images.POST("/save-video", h.saveVideoToLocalFunc)            // 暂时保持旧实现
			images.GET("/file/:id", h.serveFundusImageFile)               // 提供图片/视频文件
			images.GET("/file/thumbnail/:id", h.serveThumbnailFile)       // 提供缩略图文件
			images.GET("/:id", imageHandlers.GetImage)                    // 切换到新实现
			images.PUT("/:id", imageHandlers.UpdateImage)                 // 切换到新实现
			images.DELETE("/:id", imageHandlers.DeleteImage)              // 切换到新实现
		}

		// 诊断记录路由
		diagnosis := api.Group("/diagnosis")
		diagnosis.Use(h.authMiddleware())
		{
			diagnosis.GET("/record", diagnosisHandlers.GetDiagnosisRecord)           // 切换到新实现
			diagnosis.POST("/record", diagnosisHandlers.SaveDiagnosisRecord)         // 切换到新实现
			diagnosis.DELETE("/record/:id", diagnosisHandlers.DeleteDiagnosisRecord) // 切换到新实现
			diagnosis.GET("/ai", diagnosisHandlers.GetAIDiagnoses)                   // 切换到新实现
			diagnosis.POST("/ai/analyze", diagnosisHandlers.PerformAIDiagnosis)      // 切换到新实现
		}

		// 用户管理路由
		users := api.Group("/users")
		users.Use(h.authMiddleware())
		{
			users.GET("", userHandlers.GetUsers)                      // 切换到新实现
			users.POST("", userHandlers.CreateUser)                   // 切换到新实现
			users.GET("/:id", userHandlers.GetUser)                   // 切换到新实现
			users.PUT("/:id", userHandlers.UpdateUser)                // 切换到新实现
			users.DELETE("/:id", userHandlers.DeleteUser)             // 切换到新实现
			users.PATCH("/:id/status", userHandlers.UpdateUserStatus) // 切换到新实现
			users.GET("/:id/roles", h.getUserRoles)                   // 暂时保持旧实现
			users.PUT("/:id/roles", h.updateUserRoles)                // 暂时保持旧实现
		}

		// 角色管理路由
		roles := api.Group("/roles")
		roles.Use(h.authMiddleware())
		{
			roles.GET("", roleHandlers.GetRoles)                   // 切换到新实现
			roles.POST("", roleHandlers.CreateRole)                // 切换到新实现
			roles.GET("/:id", roleHandlers.GetRole)                // 切换到新实现
			roles.PUT("/:id", roleHandlers.UpdateRole)             // 切换到新实现
			roles.DELETE("/:id", roleHandlers.DeleteRole)          // 切换到新实现
			roles.GET("/:id/permissions", h.getRolePermissions)    // 暂时保持旧实现
			roles.PUT("/:id/permissions", h.updateRolePermissions) // 暂时保持旧实现
		}

		// 权限管理路由
		permissions := api.Group("/permissions")
		permissions.Use(h.authMiddleware())
		{
			permissions.GET("", permissionHandlers.GetPermissions) // 切换到新实现
		}

		// 第三方服务代理路由
		proxy := api.Group("/proxy")
		{
			// 系统相关代理
			proxy.GET("/system/info", h.proxyGetSystemInfo)
			proxy.POST("/system/dialog/message", h.proxyShowMessageDialog)
			proxy.POST("/system/dialog/save", h.proxyShowSaveFileDialog)
			proxy.POST("/system/dialog/open", h.proxyShowOpenFileDialog)

			// 硬件控制代理
			proxy.POST("/hardware/start", h.proxyStartHardwareDevice)
			proxy.POST("/hardware/stop", h.proxyStopHardwareDevice)
			proxy.POST("/hardware/reset", h.proxyResetHardwareDevice)
			proxy.GET("/hardware/status", h.proxyGetHardwareDeviceStatus)
			proxy.GET("/hardware/info", h.proxyGetHardwareDeviceInfo)

			// 相机控制代理
			proxy.POST("/camera/gain", h.proxySetCameraGain)
			proxy.POST("/camera/restart", h.proxyRestartCamera)

			// 壁纸控制代理
			proxy.POST("/wallpaper", h.proxySetWallpaperPosition)

			// osd状态获取代理
			proxy.GET("/hardware/status/osd", h.proxyOSD)

			// 拍照
			proxy.POST("/capture", h.proxyCaptureImage)
		}
	}

	// 创建HTTP服务器
	h.server = &http.Server{
		Addr:         ":" + port,
		Handler:      router,
		ReadTimeout:  15 * time.Second,
		WriteTimeout: 15 * time.Second,
		IdleTimeout:  60 * time.Second,
	}

	logging.Logger().Infof("HTTP服务器启动在端口 %s", port)
	return h.server.ListenAndServe()
}

// Stop 停止HTTP服务器
func (h *HTTPServer) Stop() error {
	if h.server == nil {
		return nil
	}

	ctx, cancel := context.WithTimeout(context.Background(), 5*time.Second)
	defer cancel()

	return h.server.Shutdown(ctx)
}

// healthCheck 健康检查
func (h *HTTPServer) healthCheck(c *gin.Context) {
	c.JSON(http.StatusOK, gin.H{
		"status":    "ok",
		"timestamp": time.Now().Unix(),
		"service":   "eyes_remk_api",
		"version":   "1.0.0",
	})
}

// getUserIDFromContext 从Gin上下文中安全地获取用户ID
func (h *HTTPServer) getUserIDFromContext(c *gin.Context) *uint {
	userID, exists := c.Get("user_id")
	if !exists || userID == nil {
		return nil
	}

	if uid, ok := userID.(uint); ok {
		return &uid
	}

	return nil
}

// authMiddleware JWT认证中间件
func (h *HTTPServer) authMiddleware() gin.HandlerFunc {
	return func(c *gin.Context) {
		// 获取Authorization头
		authHeader := c.GetHeader("Authorization")
		if authHeader == "" {
			c.JSON(http.StatusUnauthorized, models.APIResponse{
				Code: 401,
				Msg:  "缺少认证令牌",
			})
			c.Abort()
			return
		}

		// 检查Bearer格式
		const bearerPrefix = "Bearer "
		if len(authHeader) < len(bearerPrefix) || authHeader[:len(bearerPrefix)] != bearerPrefix {
			c.JSON(http.StatusUnauthorized, models.APIResponse{
				Code: 401,
				Msg:  "令牌格式错误",
			})
			c.Abort()
			return
		}

		// 提取令牌
		token := authHeader[len(bearerPrefix):]

		// 验证令牌
		claims, err := h.authService.ValidateToken(token)
		if err != nil {
			c.JSON(http.StatusUnauthorized, models.APIResponse{
				Code: 401,
				Msg:  "令牌无效或已过期",
			})
			c.Abort()
			return
		}

		// 将用户信息存储到上下文 (使用 "userID" 键与 handlers 保持一致)
		c.Set("userID", claims.UserID)
		c.Set("user_id", claims.UserID) // 保持向后兼容
		c.Set("username", claims.Username)
		c.Set("user_type", claims.UserType)
		c.Set("permissions", claims.Permissions)

		c.Next()
	}
}

// ===== 诊断记录相关方法包装器 =====

// ===== 第三方服务代理处理方法 =====

// 系统相关代理方法

func (h *HTTPServer) proxyGetSystemInfo(c *gin.Context) {
	response, err := h.proxy.GetSystemInfo()
	if err != nil {
		c.JSON(http.StatusInternalServerError, proxy.ProxyResponse{
			Code: 500,
			Msg:  fmt.Sprintf("获取系统信息失败: %v", err),
		})
		return
	}
	c.JSON(response.Code, response)
}

func (h *HTTPServer) proxyShowMessageDialog(c *gin.Context) {
	var req struct {
		Title   string `json:"title"`
		Message string `json:"message"`
	}
	if err := c.ShouldBindJSON(&req); err != nil {
		c.JSON(http.StatusBadRequest, proxy.ProxyResponse{
			Code: 400,
			Msg:  "请求参数错误",
		})
		return
	}

	response, err := h.proxy.ShowMessageDialog(req.Title, req.Message)
	if err != nil {
		c.JSON(http.StatusInternalServerError, proxy.ProxyResponse{
			Code: 500,
			Msg:  fmt.Sprintf("显示消息对话框失败: %v", err),
		})
		return
	}
	c.JSON(response.Code, response)
}

func (h *HTTPServer) proxyShowSaveFileDialog(c *gin.Context) {
	var req struct {
		DefaultFilename string `json:"default_filename"`
	}
	if err := c.ShouldBindJSON(&req); err != nil {
		c.JSON(http.StatusBadRequest, proxy.ProxyResponse{
			Code: 400,
			Msg:  "请求参数错误",
		})
		return
	}

	response, err := h.proxy.ShowSaveFileDialog(req.DefaultFilename)
	if err != nil {
		c.JSON(http.StatusInternalServerError, proxy.ProxyResponse{
			Code: 500,
			Msg:  fmt.Sprintf("显示保存文件对话框失败: %v", err),
		})
		return
	}
	c.JSON(response.Code, response)
}

func (h *HTTPServer) proxyShowOpenFileDialog(c *gin.Context) {
	response, err := h.proxy.ShowOpenFileDialog()
	if err != nil {
		c.JSON(http.StatusInternalServerError, proxy.ProxyResponse{
			Code: 500,
			Msg:  fmt.Sprintf("显示打开文件对话框失败: %v", err),
		})
		return
	}
	c.JSON(response.Code, response)
}

// 硬件控制代理方法

func (h *HTTPServer) proxyStartHardwareDevice(c *gin.Context) {
	response, err := h.proxy.StartHardwareDevice()
	if err != nil {
		c.JSON(http.StatusInternalServerError, proxy.ProxyResponse{
			Code: 500,
			Msg:  fmt.Sprintf("启动硬件设备失败: %v", err),
		})
		return
	}
	c.JSON(response.Code, response)
}

func (h *HTTPServer) proxyStopHardwareDevice(c *gin.Context) {
	response, err := h.proxy.StopHardwareDevice()
	if err != nil {
		c.JSON(http.StatusInternalServerError, proxy.ProxyResponse{
			Code: 500,
			Msg:  fmt.Sprintf("停止硬件设备失败: %v", err),
		})
		return
	}
	c.JSON(response.Code, response)
}

func (h *HTTPServer) proxyResetHardwareDevice(c *gin.Context) {
	response, err := h.proxy.ResetHardwareDevice()
	if err != nil {
		c.JSON(http.StatusInternalServerError, proxy.ProxyResponse{
			Code: 500,
			Msg:  fmt.Sprintf("复位硬件设备失败: %v", err),
		})
		return
	}
	c.JSON(response.Code, response)
}

func (h *HTTPServer) proxyGetHardwareDeviceStatus(c *gin.Context) {
	response, err := h.proxy.GetHardwareDeviceStatus()
	if err != nil {
		c.JSON(http.StatusInternalServerError, proxy.ProxyResponse{
			Code: 500,
			Msg:  fmt.Sprintf("获取设备状态失败: %v", err),
		})
		return
	}
	c.JSON(response.Code, response)
}

func (h *HTTPServer) proxyGetHardwareDeviceInfo(c *gin.Context) {
	response, err := h.proxy.GetHardwareDeviceInfo()
	if err != nil {
		c.JSON(http.StatusInternalServerError, proxy.ProxyResponse{
			Code: 500,
			Msg:  fmt.Sprintf("获取设备信息失败: %v", err),
		})
		return
	}
	c.JSON(response.Code, response)
}

func (h *HTTPServer) proxyCaptureImage(c *gin.Context) {
	var req struct {
		Mode       string `json:"mode" binding:"required"`
		Folderpath string `json:"folderpath" binding:"required"`
	}
	if err := c.ShouldBindJSON(&req); err != nil {
		c.JSON(http.StatusBadRequest, proxy.ProxyResponse{
			Code: 400,
			Msg:  "请求参数错误",
		})
		return
	}

	response, err := h.proxy.CaptureImage(req.Mode, req.Folderpath)
	if err != nil {
		c.JSON(http.StatusInternalServerError, proxy.ProxyResponse{
			Code: 500,
			Msg:  fmt.Sprintf("拍照失败: %v", err),
		})
		return
	}
	c.JSON(response.Code, response)
}

// proxySetCameraGain 代理设置相机增益
func (h *HTTPServer) proxySetCameraGain(c *gin.Context) {
	var requestBody struct {
		Analog  int `json:"analog"`
		Digital int `json:"digital"`
	}

	if err := c.ShouldBindJSON(&requestBody); err != nil {
		c.JSON(http.StatusBadRequest, proxy.ProxyResponse{
			Code: 400,
			Msg:  "无效的请求参数",
		})
		return
	}

	response, err := h.proxy.SetCameraGain(requestBody.Analog, requestBody.Digital)
	if err != nil {
		c.JSON(http.StatusInternalServerError, proxy.ProxyResponse{
			Code: 500,
			Msg:  fmt.Sprintf("设置相机增益失败: %v", err),
		})
		return
	}
	c.JSON(response.Code, response)
}

// proxyRestartCamera 代理重启相机
func (h *HTTPServer) proxyRestartCamera(c *gin.Context) {
	response, err := h.proxy.RestartCamera()
	if err != nil {
		c.JSON(http.StatusInternalServerError, proxy.ProxyResponse{
			Code: 500,
			Msg:  fmt.Sprintf("重启相机失败: %v", err),
		})
		return
	}
	c.JSON(response.Code, response)
}

// proxyOSD 获取OSD状态
func (h *HTTPServer) proxyOSD(c *gin.Context) {
	response, err := h.proxy.Osd()
	if err != nil {
		c.JSON(http.StatusInternalServerError, proxy.ProxyResponse{
			Code: 500,
			Msg:  fmt.Sprintf("获取OSD状态失败: %v", err),
		})
		return
	}
	c.JSON(response.Code, response)
}

// proxySetWallpaperPosition 代理设置壁纸位置
func (h *HTTPServer) proxySetWallpaperPosition(c *gin.Context) {
	var req struct {
		Pos string `json:"pos" binding:"required,oneof=上 下 左 右 左中 右中"`
	}

	if err := c.ShouldBindJSON(&req); err != nil {
		c.JSON(http.StatusBadRequest, proxy.ProxyResponse{
			Code: 400,
			Msg:  "请求参数错误，pos必须是上 下 左 右 左中 右中",
		})
		return
	}

	response, err := h.proxy.SetWallpaperPosition(req.Pos)
	if err != nil {
		c.JSON(http.StatusInternalServerError, proxy.ProxyResponse{
			Code: 500,
			Msg:  fmt.Sprintf("设置壁纸位置失败: %v", err),
		})
		return
	}
	c.JSON(response.Code, response)
}

// requestLoggerMiddleware 请求日志中间件
func (h *HTTPServer) requestLoggerMiddleware() gin.HandlerFunc {
	return gin.LoggerWithFormatter(func(param gin.LogFormatterParams) string {
		// 获取请求体
		var requestBody string
		if param.Request.Body != nil {
			bodyBytes, _ := io.ReadAll(param.Request.Body)
			param.Request.Body = io.NopCloser(bytes.NewBuffer(bodyBytes))
			if len(bodyBytes) > 0 {
				requestBody = string(bodyBytes)
			}
		}

		// 记录请求信息
		logging.Logger().Infof("🌐 ========== HTTP请求 ==========")
		logging.Logger().Infof("🌐 请求方法: %s", param.Method)
		logging.Logger().Infof("🌐 请求路径: %s", param.Path)
		logging.Logger().Infof("🌐 请求URL: %s", param.Request.URL.String())
		logging.Logger().Infof("🌐 客户端IP: %s", param.ClientIP)
		logging.Logger().Infof("🌐 用户代理: %s", param.Request.UserAgent())
		if requestBody != "" {
			logging.Logger().Infof("🌐 请求体: %s", requestBody)
		} else {
			logging.Logger().Infof("🌐 请求体: (无)")
		}
		logging.Logger().Infof("🌐 响应状态: %d", param.StatusCode)
		logging.Logger().Infof("🌐 响应时间: %v", param.Latency)
		logging.Logger().Infof("🌐 ==============================")

		return ""
	})
}

// updateRegistrationStatus 更新挂号状态
func (h *HTTPServer) updateRegistrationStatus(c *gin.Context) {
	id, err := strconv.ParseUint(c.Param("id"), 10, 32)
	if err != nil {
		c.JSON(http.StatusBadRequest, models.ErrorResponse(400, "无效的挂号ID"))
		return
	}

	var req struct {
		Status string `json:"status" binding:"required,oneof=unsigned present confirmed checked_in in_progress completed cancelled registered"`
	}
	if err := c.ShouldBindJSON(&req); err != nil {
		c.JSON(http.StatusBadRequest, models.ErrorResponse(400, "请求参数错误"))
		return
	}

	var registration models.Registration
	if err := h.database.DB.Where("registrations.deleted_at IS NULL").First(&registration, uint(id)).Error; err != nil {
		if err == gorm.ErrRecordNotFound {
			c.JSON(http.StatusNotFound, models.ErrorResponse(404, "挂号记录不存在"))
			return
		}
		c.JSON(http.StatusInternalServerError, models.ErrorResponse(500, "查询挂号记录失败"))
		return
	}

	// 更新状态
	updates := map[string]interface{}{
		"status": req.Status,
	}

	// 如果是签到状态，记录签到时间
	if req.Status == "checked_in" {
		updates["check_in_time"] = time.Now()
	}

	// 获取用户ID用于记录更新人
	if userID := h.getUserIDFromContext(c); userID != nil {
		updates["updated_by"] = userID
	}

	if err := h.database.DB.Model(&registration).Updates(updates).Error; err != nil {
		c.JSON(http.StatusInternalServerError, models.ErrorResponse(500, "更新挂号状态失败"))
		return
	}

	// 记录操作日志
	username, _ := c.Get("username")
	if userID := h.getUserIDFromContext(c); userID != nil {
		h.authService.LogOperation("INFO", "REGISTRATION", "更新挂号状态", userID, map[string]interface{}{
			"username":        username,
			"registration_id": registration.ID,
			"old_status":      registration.Status,
			"new_status":      req.Status,
			"ip_address":      c.ClientIP(),
		})
	}

	c.JSON(http.StatusOK, models.APIResponse{
		Code: 200,
		Msg:  "挂号状态更新成功",
		Data: registration,
	})
}

// saveImageToLocalFunc 图片保存到本地
func (h *HTTPServer) saveImageToLocalFunc(c *gin.Context) {
	var req struct {
		ExaminationID     uint   `json:"examination_id" binding:"required"`
		FileDir           string `json:"file_dir" binding:"required"`
		ImageName         string `json:"image_name" binding:"required"`
		EyeSide           string `json:"eye_side" binding:"required,oneof=OD OS"`
		ImageType         string `json:"image_type"`
		Resolution        string `json:"resolution"`
		FileFormat        string `json:"file_format" binding:"required"`
		AcquisitionDevice string `json:"acquisition_device"`
		CaptureMode       string `json:"capture_mode" binding:"required,oneof=gray color"`
	}

	if err := c.ShouldBindJSON(&req); err != nil {
		c.JSON(http.StatusBadRequest, models.ErrorResponseWithDetail(400, "请求参数错误", err.Error()))
		return
	}

	// 生成影像编号
	imageNumber := fmt.Sprintf("FI%s%d", time.Now().Format("20060102150405"), req.ExaminationID)
	// 获取用户ID
	userID := h.getUserIDFromContext(c)
	// 使用原始SQL插入，因为数据库表结构与models不完全匹配
	insertSQL := `
		INSERT INTO fundus_images (
			examination_id, image_number, eye_side, capture_mode, image_type, 
			file_path, file_name, file_size, file_format, 
			acquisition_device, upload_status, thumbnail_data, created_by,
			created_at, updated_at
		) VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, $12, $13, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP)
		RETURNING id
	`
	var insertedID uint
	// 获取文件大小
	tmpReadPath := filepath.Join(req.FileDir, req.ImageName)
	// 打开文件
	file, err := os.Open(tmpReadPath)
	if err != nil {
		panic(fmt.Errorf("打开图片失败: %v", err))
	}
	defer file.Close()
	// 获取文件信息（大小）
	info, _ := file.Stat()
	img_size := info.Size()

	// 转为 Base64
	thumbnailData, err := ImgPathToBase64(tmpReadPath)
	if err != nil {
		panic(fmt.Errorf("转换图片为Base64失败: %v", err))
	}

	err = h.database.DB.Raw(insertSQL,
		req.ExaminationID,
		imageNumber,
		req.EyeSide,
		req.CaptureMode,
		req.ImageType,
		req.FileDir,
		req.ImageName,
		img_size,
		req.FileFormat,
		req.AcquisitionDevice,
		"uploaded",
		thumbnailData, // 添加缩略图数据
		userID,
	).Scan(&insertedID).Error

	if err != nil {
		// 如果数据库保存失败，删除已保存的文件
		os.Remove(tmpReadPath)
		c.JSON(http.StatusInternalServerError, models.ErrorResponseWithDetail(500, "保存图像记录失败", err.Error()))
		return
	}
	// 记录操作日志
	username, _ := c.Get("username")
	if userID != nil {
		h.authService.LogOperation("INFO", "IMAGE", "保存图像到本地", userID, map[string]interface{}{
			"username":       username,
			"examination_id": req.ExaminationID,
			"image_id":       insertedID,
			"eye_side":       req.EyeSide,
			"file_name":      req.ImageName,
			"file_size":      img_size,
			"ip_address":     c.ClientIP(),
		})
	}
	c.JSON(http.StatusOK, models.APIResponse{
		Code: 200,
		Msg:  "图像保存成功",
		Data: map[string]interface{}{
			"id":            insertedID,
			"image_number":  imageNumber,
			"image_path":    tmpReadPath,
			"thumbnailData": thumbnailData,
			"capture_mode":  req.CaptureMode,
		},
	})
}
func GenColorFilename() string {
	return fmt.Sprintf("%s_color.jpg", time.Now().Format("150405"))
}
func ImgPathToBase64(imgPath string) (string, error) {
	// 打开文件
	file, err := os.Open(imgPath)
	if err != nil {
		return "", fmt.Errorf("打开图片失败: %v", err)
	}
	defer file.Close()
	// 解码图片
	img, format, err := image.Decode(file)
	if err != nil {
		return "", fmt.Errorf("解析图片失败: %v", err)
	}
	// 压缩图片（根据格式处理）
	var buf bytes.Buffer
	switch format {
	case "jpeg":
		// 压缩 JPEG：quality 取值范围 1-100
		err = jpeg.Encode(&buf, img, &jpeg.Options{Quality: 40})
	case "png":
		// 压缩 PNG：使用 Encoder 设置压缩等级
		encoder := png.Encoder{CompressionLevel: png.BestCompression}
		err = encoder.Encode(&buf, img)
	default:
		return "", fmt.Errorf("不支持的图片格式: %s", format)
	}
	if err != nil {
		return "", fmt.Errorf("压缩图片失败: %v", err)
	}
	// 转为 Base64
	thumbnailData := base64.StdEncoding.EncodeToString(buf.Bytes())
	return thumbnailData, nil
}

type ImgInfoInsertDB struct {
	ExaminationID     uint
	ImageNumber       string
	EyeSide           string
	CaptureMode       string
	ImageType         string
	FileDir           string
	ImageName         string
	ImgSize           int64
	FileFormat        string
	AcquisitionDevice string
	ThumbnailData     string
	UserID            uint
}

type ImageInfo struct {
	ID            uint   `json:"id"`
	ImagePath     string `json:"image_path"`
	ThumbnailData string `json:"thumbnail_data"`
}

type ColorModeRespones struct {
	Images      []ImageInfo `json:"images"`
	CaptureMode string      `json:"capture_mode"`
	ImageNumber string      `json:"image_number"`
}

func InsertImgInfoInDB(db *database.Database, ImgInfoInsertDB ImgInfoInsertDB) (uint, error) {
	insertSQL := `
		INSERT INTO fundus_images (
			examination_id, image_number, eye_side, capture_mode, image_type, 
			file_path, file_name, file_size, file_format, 
			acquisition_device, upload_status, thumbnail_data, created_by,
			created_at, updated_at
		) VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, $12, $13, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP)
		RETURNING id
	`
	var insertedID uint
	err := db.DB.Raw(insertSQL,
		ImgInfoInsertDB.ExaminationID,
		ImgInfoInsertDB.ImageNumber,
		ImgInfoInsertDB.EyeSide,
		ImgInfoInsertDB.CaptureMode,
		ImgInfoInsertDB.ImageType,
		ImgInfoInsertDB.FileDir,
		ImgInfoInsertDB.ImageName,
		ImgInfoInsertDB.ImgSize,
		ImgInfoInsertDB.FileFormat,
		ImgInfoInsertDB.AcquisitionDevice,
		"uploaded",
		ImgInfoInsertDB.ThumbnailData, // 添加缩略图数据
		ImgInfoInsertDB.UserID,
	).Scan(&insertedID).Error
	if err != nil {
		return 0, fmt.Errorf("插入图像记录失败: %v", err)
	}
	logging.Logger().Infof("插入图像记录成功: %d", insertedID)
	return insertedID, nil
}

// saveMultiImageToLocalFunc 多图片保存到本地
func (h *HTTPServer) saveMultiImageToLocalFunc(c *gin.Context) {
	var req struct {
		ExaminationID     uint     `json:"examination_id" binding:"required"`
		FileDir           string   `json:"file_dir" binding:"required"`
		ImageName         []string `json:"image_name" binding:"required"`
		EyeSide           string   `json:"eye_side" binding:"required,oneof=OD OS"`
		ImageType         string   `json:"image_type"`
		Resolution        string   `json:"resolution"`
		FileFormat        string   `json:"file_format" binding:"required"`
		AcquisitionDevice string   `json:"acquisition_device"`
		CaptureMode       string   `json:"capture_mode" binding:"required,oneof=gray color"`
	}

	if err := c.ShouldBindJSON(&req); err != nil {
		c.JSON(http.StatusBadRequest, models.ErrorResponseWithDetail(400, "请求参数错误", err.Error()))
		return
	}

	// 生成影像编号
	imageNumber := fmt.Sprintf("FI%s%d", time.Now().Format("20060102150405"), req.ExaminationID)
	// 获取用户ID
	userID := h.getUserIDFromContext(c)

	var ir_img string
	var green_img string
	var red_img string
	var blue_img string
	var color_mod_resp ColorModeRespones
	color_mod_resp.CaptureMode = req.CaptureMode
	color_mod_resp.ImageNumber = imageNumber
	for _, img_name := range req.ImageName {
		var imgInfo ImageInfo
		if strings.HasSuffix(img_name, "_G.jpg") {
			green_img = filepath.Join(req.FileDir, img_name)
		}
		if strings.HasSuffix(img_name, "_IR.jpg") {
			ir_img = filepath.Join(req.FileDir, img_name)
		}
		if strings.HasSuffix(img_name, "_R.jpg") {
			red_img = filepath.Join(req.FileDir, img_name)
		}
		if strings.HasSuffix(img_name, "_B.jpg") {
			blue_img = filepath.Join(req.FileDir, img_name)
		}
		// 获取文件大小
		tmpReadPath := filepath.Join(req.FileDir, img_name)
		// 打开文件
		file, err := os.Open(tmpReadPath)
		if err != nil {
			panic(fmt.Errorf("打开图片失败: %v", err))
		}
		defer file.Close()
		imgInfo.ImagePath = tmpReadPath
		// 获取文件信息（大小）
		info, _ := file.Stat()
		img_size := info.Size()

		// 转为 Base64
		tmpThumbnailData, err := ImgPathToBase64(tmpReadPath)
		if err != nil {
			panic(fmt.Errorf("转换图片为Base64失败: %v", err))
		}
		imgInfo.ThumbnailData = tmpThumbnailData

		var insertedID uint

		insertedID, err = InsertImgInfoInDB(h.database, ImgInfoInsertDB{
			ExaminationID:     req.ExaminationID,
			ImageNumber:       imageNumber,
			EyeSide:           req.EyeSide,
			CaptureMode:       req.CaptureMode,
			ImageType:         req.ImageType,
			FileDir:           req.FileDir,
			ImageName:         img_name,
			ImgSize:           img_size,
			FileFormat:        req.FileFormat,
			AcquisitionDevice: req.AcquisitionDevice,
			ThumbnailData:     tmpThumbnailData,
			UserID:            *userID,
		})
		if err != nil {
			// 如果数据库保存失败，删除已保存的文件
			os.Remove(tmpReadPath)
			c.JSON(http.StatusInternalServerError, models.ErrorResponseWithDetail(500, "保存图像记录失败", err.Error()))
			return
		}
		imgInfo.ID = insertedID
		color_mod_resp.Images = append(color_mod_resp.Images, imgInfo)
		// 记录操作日志
		username, _ := c.Get("username")
		if userID != nil {
			h.authService.LogOperation("INFO", "IMAGE", "保存图像到本地", userID, map[string]interface{}{
				"username":       username,
				"examination_id": req.ExaminationID,
				"image_id":       insertedID,
				"eye_side":       req.EyeSide,
				"file_name":      img_name,
				"file_size":      img_size,
				"ip_address":     c.ClientIP(),
			})
		}

	}
	// 打印 ir_img, green_img, red_img, blue_img
	logging.Logger().Infof("ir_img:", ir_img)
	logging.Logger().Infof("green_img:", green_img)
	logging.Logger().Infof("red_img:", red_img)
	logging.Logger().Infof("blue_img:", blue_img)
	// ai合成
	// var thumbnailData string
	ai_img_name := GenColorFilename()
	ai_img_path := filepath.Join(req.FileDir, ai_img_name)
	// 发起请求到url：http://localhost:8088/api/colorize
	// 请求体json:{"ir_image":ir_img,"green_image":green_img,"red_image":red_img,"blue_image":blue_img}
	// 响应体：{"code":200,"msg":"图像保存成功","data":{"save_path":ai_img_path}}
	reqBody := map[string]string{
		"color_img_path": ai_img_path,
		"ir_image":       ir_img,
		"green_image":    green_img,
		"red_image":      red_img,
		"blue_image":     blue_img,
	}
	// 发起请求
	reqBodyStr, err := json.Marshal(reqBody)
	if err != nil {
		logging.Logger().Errorf("编码请求体失败: %v", err)
		panic(fmt.Errorf("编码请求体失败: %v", err))
	}
	resp, err := http.Post("http://localhost:8088/api/colorize", "application/json", bytes.NewBuffer(reqBodyStr))
	if err != nil {
		logging.Logger().Errorf("发起请求失败: %v", err)
		panic(fmt.Errorf("发起请求失败: %v", err))
	}
	defer resp.Body.Close()
	// 响应体json：{"code":200,"msg":"图像保存成功","data":{"save_path":ai_img_path}}
	var respBody models.APIResponse
	if err := json.NewDecoder(resp.Body).Decode(&respBody); err != nil {
		logging.Logger().Errorf("解码响应体失败: %v", err)
		panic(fmt.Errorf("解码响应体失败: %v", err))
	}
	logging.Logger().Infof("响应体: %v", respBody)
	// 检查响应码
	if respBody.Code != 200 {
		logging.Logger().Errorf("请求失败: %s", respBody.Msg)
		panic(fmt.Errorf("请求失败: %s", respBody.Msg))
	}
	dataMap, ok := respBody.Data.(map[string]interface{})
	if !ok {
		panic("data 不是 map[string]interface{} 类型")
	}
	logging.Logger().Infof("save_path: %s", dataMap["save_path"])
	savePath, ok := dataMap["save_path"].(string)
	if !ok {
		panic("save_path 不是字符串类型")
	}

	if savePath != ai_img_path {
		logging.Logger().Errorf("返回的路径与请求的不一致: %s", savePath)
		panic("save_path 与请求的不一致")
	}
	ai_img_thumbnailData, err := ImgPathToBase64(savePath)
	if err != nil {
		logging.Logger().Errorf("转换图片为Base64失败: %v", err)
		panic(fmt.Errorf("转换图片为Base64失败: %v", err))
	}
	var insertedID uint
	// 获取文件大小
	colorReadPath := filepath.Join(req.FileDir, ai_img_name)
	// 打开文件
	file, err := os.Open(colorReadPath)
	if err != nil {
		logging.Logger().Errorf("打开图片失败: %v", err)
		panic(fmt.Errorf("打开图片失败: %v", err))
	}
	defer file.Close()
	// 获取文件信息（大小）
	info, _ := file.Stat()
	ai_img_size := info.Size()
	logging.Logger().Infof("ai_img_size: %d", ai_img_size)
	insertedID, err = InsertImgInfoInDB(h.database, ImgInfoInsertDB{
		ExaminationID:     req.ExaminationID,
		ImageNumber:       imageNumber,
		EyeSide:           req.EyeSide,
		CaptureMode:       req.CaptureMode,
		ImageType:         req.ImageType,
		FileDir:           req.FileDir,
		ImageName:         ai_img_name,
		ImgSize:           ai_img_size,
		FileFormat:        req.FileFormat,
		AcquisitionDevice: req.AcquisitionDevice,
		ThumbnailData:     ai_img_thumbnailData,
		UserID:            *userID,
	})
	// 记录操作日志
	username, _ := c.Get("username")
	logging.Logger().Infof("username: %s", username)
	if userID != nil {
		h.authService.LogOperation("INFO", "IMAGE", "保存图像到本地", userID, map[string]interface{}{
			"username":       username,
			"examination_id": req.ExaminationID,
			"image_id":       insertedID,
			"eye_side":       req.EyeSide,
			"file_name":      ai_img_name,
			"file_size":      ai_img_size,
			"ip_address":     c.ClientIP(),
		})
	}
	var colorImgInfo ImageInfo
	colorImgInfo.ID = insertedID
	colorImgInfo.ImagePath = colorReadPath
	colorImgInfo.ThumbnailData = ai_img_thumbnailData
	color_mod_resp.Images = append(color_mod_resp.Images, colorImgInfo)
	c.JSON(http.StatusOK, models.APIResponse{
		Code: 200,
		Msg:  "图像保存成功",
		Data: color_mod_resp,
	})
}

// saveVideoToLocalFunc 保存视频到本地
func (h *HTTPServer) saveVideoToLocalFunc(c *gin.Context) {
	var req struct {
		ExaminationID     uint   `json:"examination_id" binding:"required"`
		PatientID         string `json:"patient_id" binding:"required"`
		VideoData         string `json:"video_data" binding:"required"`
		CoverImageData    string `json:"cover_image_data" binding:"required"`
		EyeSide           string `json:"eye_side" binding:"required,oneof=OD OS"`
		Duration          int    `json:"duration" binding:"required"`
		FileFormat        string `json:"file_format" binding:"required,oneof=webm mp4 ogv mov"`
		AcquisitionDevice string `json:"acquisition_device" binding:"required"`
		CaptureMode       string `json:"capture_mode" binding:"required,oneof=gray color"`
	}

	if err := c.ShouldBindJSON(&req); err != nil {
		c.JSON(http.StatusBadRequest, models.ErrorResponseWithDetail(400, "请求参数错误", err.Error()))
		return
	}

	// 解码base64视频数据
	videoData := req.VideoData
	if strings.HasPrefix(videoData, "data:video/") {
		parts := strings.Split(videoData, ",")
		if len(parts) > 1 {
			videoData = parts[1]
		}
	}

	decodedData, err := base64.StdEncoding.DecodeString(videoData)
	if err != nil {
		c.JSON(http.StatusBadRequest, models.ErrorResponseWithDetail(400, "视频数据解码失败", err.Error()))
		return
	}

	// 创建保存目录
	configManager := config.GetManager()
	baseDir := configManager.GetSaveFolderPath()
	if baseDir == "" {
		// 使用默认路径作为后备
		baseDir = "./media"
	}

	// 按照要求创建目录结构: saveFolderPath/{patient_id}/{年月日}_{examination_id}/
	now := time.Now()
	dateStr := now.Format("20060102")
	saveDir := filepath.Join(baseDir, req.PatientID, fmt.Sprintf("%s_%d", dateStr, req.ExaminationID))
	if err := os.MkdirAll(saveDir, 0755); err != nil {
		c.JSON(http.StatusInternalServerError, models.ErrorResponseWithDetail(500, "创建保存目录失败", err.Error()))
		return
	}

	// 生成文件名: {时分秒}.mp4
	timeStr := now.Format("150405")
	fileName := fmt.Sprintf("%s.%s", timeStr, req.FileFormat)
	filePath := filepath.Join(saveDir, fileName)

	// 保存文件
	if err := os.WriteFile(filePath, decodedData, 0644); err != nil {
		c.JSON(http.StatusInternalServerError, models.ErrorResponseWithDetail(500, "保存文件失败", err.Error()))
		return
	}

	// 获取文件大小
	fileInfo, _ := os.Stat(filePath)
	fileSize := fileInfo.Size()

	// 生成视频编号
	videoNumber := fmt.Sprintf("FV%s%d", time.Now().Format("20060102150405"), req.ExaminationID)

	// 获取用户ID
	userID := h.getUserIDFromContext(c)

	// 使用原始SQL插入
	insertSQL := `
		INSERT INTO fundus_images (
			examination_id, image_number, eye_side, image_type, 
			file_path, file_name, file_size, file_format, 
			acquisition_device, upload_status, created_by,
			duration,thumbnail_data,capture_mode, created_at, updated_at
		) VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, $12,$13,$14 CURRENT_TIMESTAMP, CURRENT_TIMESTAMP)
		RETURNING id
	`

	var insertedID uint
	err = h.database.DB.Raw(insertSQL,
		req.ExaminationID,
		videoNumber,
		req.EyeSide,
		"video",
		filePath,
		fileName,
		fileSize,
		req.FileFormat,
		req.AcquisitionDevice,
		"uploaded",
		userID,
		req.Duration,
		req.CoverImageData,
		req.CaptureMode,
	).Scan(&insertedID).Error

	if err != nil {
		// 如果数据库保存失败，删除已保存的文件
		os.Remove(filePath)
		c.JSON(http.StatusInternalServerError, models.ErrorResponseWithDetail(500, "保存视频记录失败", err.Error()))
		return
	}

	// 记录操作日志
	username, _ := c.Get("username")
	if userID != nil {
		h.authService.LogOperation("INFO", "VIDEO", "保存视频到本地", userID, map[string]interface{}{
			"username":       username,
			"examination_id": req.ExaminationID,
			"video_id":       insertedID,
			"eye_side":       req.EyeSide,
			"file_name":      fileName,
			"file_size":      fileSize,
			"duration":       req.Duration,
			"ip_address":     c.ClientIP(),
		})
	}

	c.JSON(http.StatusOK, models.APIResponse{
		Code: 200,
		Msg:  "视频保存成功",
		Data: map[string]interface{}{
			"id":           insertedID,
			"video_number": videoNumber,
			"file_path":    filePath,
			"file_name":    fileName,
			"file_size":    fileSize,
			"capture_mode": req.CaptureMode,
		},
	})
}

// serveFundusImageFile 提供眼底图像文件访问
func (h *HTTPServer) serveFundusImageFile(c *gin.Context) {
	id, err := strconv.ParseUint(c.Param("id"), 10, 32)
	if err != nil {
		c.JSON(http.StatusBadRequest, models.ErrorResponse(400, "无效的图像ID"))
		return
	}

	// 查询数据库获取文件路径
	var image struct {
		FilePath string `gorm:"column:file_path"`
		FileName string `gorm:"column:file_name"`
	}

	err = h.database.DB.Table("fundus_images").
		Select("file_path, file_name").
		Where("id = ?", id).
		First(&image).Error

	if err != nil {
		if err == gorm.ErrRecordNotFound {
			c.JSON(http.StatusNotFound, models.ErrorResponse(404, "图像不存在"))
		} else {
			c.JSON(http.StatusInternalServerError, models.ErrorResponse(500, "查询图像失败"))
		}
		return
	}

	// 检查文件是否存在
	if _, err := os.Stat(image.FilePath); os.IsNotExist(err) {
		c.JSON(http.StatusNotFound, models.ErrorResponse(404, "文件不存在"))
		return
	}

	// 返回文件
	c.File(image.FilePath)
}

// serveThumbnailFile 提供缩略图文件访问
func (h *HTTPServer) serveThumbnailFile(c *gin.Context) {
	id, err := strconv.ParseUint(c.Param("id"), 10, 32)
	if err != nil {
		c.JSON(http.StatusBadRequest, models.ErrorResponse(400, "无效的图像ID"))
		return
	}

	// 查询数据库获取缩略图路径
	var image struct {
		ThumbnailPath *string `gorm:"column:thumbnail_path"`
	}

	err = h.database.DB.Table("fundus_images").
		Select("thumbnail_path").
		Where("id = ?", id).
		First(&image).Error

	if err != nil {
		if err == gorm.ErrRecordNotFound {
			c.JSON(http.StatusNotFound, models.ErrorResponse(404, "图像不存在"))
		} else {
			c.JSON(http.StatusInternalServerError, models.ErrorResponse(500, "查询图像失败"))
		}
		return
	}

	// 检查是否有缩略图
	if image.ThumbnailPath == nil || *image.ThumbnailPath == "" {
		c.JSON(http.StatusNotFound, models.ErrorResponse(404, "缩略图不存在"))
		return
	}

	// 检查文件是否存在
	if _, err := os.Stat(*image.ThumbnailPath); os.IsNotExist(err) {
		c.JSON(http.StatusNotFound, models.ErrorResponse(404, "缩略图文件不存在"))
		return
	}

	// 返回文件
	c.File(*image.ThumbnailPath)
}

// getUserRoles 获取用户角色
func (h *HTTPServer) getUserRoles(c *gin.Context) {
	id, err := strconv.ParseUint(c.Param("id"), 10, 32)
	if err != nil {
		c.JSON(http.StatusBadRequest, models.APIResponse{
			Code: 400,
			Msg:  "用户ID格式错误",
		})
		return
	}

	var userRoles []models.UserRole
	result := h.database.DB.Preload("Role").Where("user_id = ? AND is_active = true AND deleted_at IS NULL", uint(id)).Find(&userRoles)
	if result.Error != nil {
		c.JSON(http.StatusInternalServerError, models.APIResponse{
			Code: 500,
			Msg:  "获取用户角色失败",
		})
		return
	}

	c.JSON(http.StatusOK, models.APIResponse{
		Code: 200,
		Msg:  "用户角色获取成功",
		Data: userRoles,
	})
}

// updateUserRoles 更新用户角色
func (h *HTTPServer) updateUserRoles(c *gin.Context) {
	// 检查权限
	permissions, _ := c.Get("permissions")
	permList, ok := permissions.([]string)
	if !ok || !contains(permList, "user_manage") {
		c.JSON(http.StatusForbidden, models.APIResponse{
			Code: 403,
			Msg:  "权限不足",
		})
		return
	}

	id, err := strconv.ParseUint(c.Param("id"), 10, 32)
	if err != nil {
		c.JSON(http.StatusBadRequest, models.APIResponse{
			Code: 400,
			Msg:  "用户ID格式错误",
		})
		return
	}

	var req models.UpdateUserRolesRequest
	if err := c.ShouldBindJSON(&req); err != nil {
		c.JSON(http.StatusBadRequest, models.APIResponse{
			Code: 400,
			Msg:  "请求参数错误",
		})
		return
	}

	// 开始事务
	tx := h.database.DB.Begin()

	// 删除现有角色关联
	result := tx.Where("user_id = ?", uint(id)).Delete(&models.UserRole{})
	if result.Error != nil {
		tx.Rollback()
		c.JSON(http.StatusInternalServerError, models.APIResponse{
			Code: 500,
			Msg:  "更新用户角色失败",
		})
		return
	}

	// 添加新角色关联
	userID, _ := c.Get("user_id")
	for _, roleID := range req.RoleIDs {
		userRole := models.UserRole{
			UserID:   uint(id),
			RoleID:   roleID,
			IsActive: true,
		}
		if userID != nil {
			assignedBy := userID.(uint)
			userRole.AssignedBy = &assignedBy
		}
		result = tx.Create(&userRole)
		if result.Error != nil {
			tx.Rollback()
			c.JSON(http.StatusInternalServerError, models.APIResponse{
				Msg: "更新用户角色失败",
			})
			return
		}
	}

	// 提交事务
	tx.Commit()

	// 记录操作日志
	username, _ := c.Get("username")
	userIDForLog := uint(id)
	h.authService.LogOperation("INFO", "USER", "更新用户角色", &userIDForLog, map[string]interface{}{
		"username":       username,
		"target_user_id": id,
		"role_ids":       req.RoleIDs,
		"ip_address":     c.ClientIP(),
	})

	c.JSON(http.StatusOK, models.APIResponse{
		Code: 200,
		Msg:  "用户角色更新成功",
	})
}

// getRolePermissions 获取角色权限
func (h *HTTPServer) getRolePermissions(c *gin.Context) {
	id, err := strconv.ParseUint(c.Param("id"), 10, 32)
	if err != nil {
		c.JSON(http.StatusBadRequest, models.APIResponse{
			Code: 400,
			Msg:  "角色ID格式错误",
		})
		return
	}

	var permissions []models.Permission
	result := h.database.DB.
		Select("DISTINCT permissions.*").
		Table("permissions").
		Joins("JOIN role_permissions ON permissions.id = role_permissions.permission_id").
		Where("role_permissions.role_id = ?", uint(id)).
		Where("role_permissions.is_active = true").
		Where("permissions.is_active = true").
		Where("role_permissions.deleted_at IS NULL").
		Where("permissions.deleted_at IS NULL").
		Find(&permissions)

	if result.Error != nil {
		c.JSON(http.StatusInternalServerError, models.APIResponse{
			Code: 500,
			Msg:  "获取角色权限失败",
		})
		return
	}

	c.JSON(http.StatusOK, models.APIResponse{
		Code: 200,
		Msg:  "角色权限获取成功",
		Data: permissions,
	})
}

// updateRolePermissions 更新角色权限
func (h *HTTPServer) updateRolePermissions(c *gin.Context) {
	// 检查权限
	permissions, _ := c.Get("permissions")
	permList, ok := permissions.([]string)
	if !ok || !contains(permList, "user_manage") {
		c.JSON(http.StatusForbidden, models.APIResponse{
			Code: 403,
			Msg:  "权限不足",
		})
		return
	}

	id, err := strconv.ParseUint(c.Param("id"), 10, 32)
	if err != nil {
		c.JSON(http.StatusBadRequest, models.APIResponse{
			Code: 400,
			Msg:  "角色ID格式错误",
		})
		return
	}

	var req models.UpdateRolePermissionsRequest
	if err := c.ShouldBindJSON(&req); err != nil {
		c.JSON(http.StatusBadRequest, models.APIResponse{
			Code: 400,
			Msg:  "请求参数错误",
		})
		return
	}

	// 检查角色是否存在
	var role models.Role
	result := h.database.DB.Where("id = ? AND deleted_at IS NULL", uint(id)).First(&role)
	if result.Error != nil {
		if result.Error == gorm.ErrRecordNotFound {
			c.JSON(http.StatusNotFound, models.APIResponse{
				Code: 404,
				Msg:  "角色不存在",
			})
		} else {
			c.JSON(http.StatusInternalServerError, models.APIResponse{
				Code: 500,
				Msg:  "获取角色信息失败",
			})
		}
		return
	}

	// 开始事务
	tx := h.database.DB.Begin()

	// 删除现有权限关联
	result = tx.Where("role_id = ?", uint(id)).Delete(&models.RolePermission{})
	if result.Error != nil {
		tx.Rollback()
		c.JSON(http.StatusInternalServerError, models.APIResponse{
			Code: 500,
			Msg:  "更新角色权限失败",
		})
		return
	}

	// 添加新权限关联
	userID, _ := c.Get("user_id")
	for _, permissionID := range req.PermissionIDs {
		rolePermission := models.RolePermission{
			RoleID:       uint(id),
			PermissionID: permissionID,
			IsActive:     true,
		}
		if userID != nil {
			grantedBy := userID.(uint)
			rolePermission.GrantedBy = &grantedBy
		}
		result = tx.Create(&rolePermission)
		if result.Error != nil {
			tx.Rollback()
			c.JSON(http.StatusInternalServerError, models.APIResponse{
				Code: 500,
				Msg:  "更新角色权限失败",
			})
			return
		}
	}

	// 提交事务
	tx.Commit()

	// 记录操作日志
	username, _ := c.Get("username")
	roleIDForLog := uint(id)
	h.authService.LogOperation("INFO", "ROLE", "更新角色权限", &roleIDForLog, map[string]interface{}{
		"username":       username,
		"role_id":        id,
		"permission_ids": req.PermissionIDs,
		"ip_address":     c.ClientIP(),
	})

	c.JSON(http.StatusOK, models.APIResponse{
		Code: 200,
		Msg:  "角色权限更新成功",
	})
}

// contains 检查字符串切片中是否包含指定字符串
func contains(slice []string, item string) bool {
	for _, s := range slice {
		if s == item {
			return true
		}
	}
	return false
}
