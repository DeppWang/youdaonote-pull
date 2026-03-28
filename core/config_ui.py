import os
import threading
from tkinter import BooleanVar, StringVar, Tk, messagebox, Canvas
from tkinter import filedialog
from tkinter import ttk
from tkinter import simpledialog

from core.config import (
    AppConfig,
    default_config_path,
    import_config_from_picgo,
    load_config,
    save_config,
    update_config_from_dict,
)


class ConfigWindow:
    def __init__(self, root, config: AppConfig, config_path: str, initial_message: str = ""):
        self.root = root
        self.config_path = config_path
        self.config = config
        self.status_var = StringVar(value=initial_message or "准备就绪")

        self.local_dir_var = StringVar(value=config.local_dir)
        self.ydnote_dir_var = StringVar(value=config.ydnote_dir)
        self.is_relative_path_var = BooleanVar(value=config.is_relative_path)
        self.image_uploader_var = StringVar(value=config.image_uploader)
        self.smms_secret_token_var = StringVar(value=config.smms_secret_token)
        self.picgo_config_path_var = StringVar(value=config.picgo_config_path)
        self.oss_endpoint_var = StringVar(value=config.aliyun_oss.endpoint)
        self.oss_bucket_var = StringVar(value=config.aliyun_oss.bucket)
        self.oss_access_key_id_var = StringVar(value=config.aliyun_oss.access_key_id)
        self.oss_access_key_secret_var = StringVar(value=config.aliyun_oss.access_key_secret)
        self.oss_path_var = StringVar(value=config.aliyun_oss.path)
        self.oss_custom_domain_var = StringVar(value=config.aliyun_oss.custom_domain)
        self.oss_use_https_var = BooleanVar(value=config.aliyun_oss.use_https)

        # Cookies 变量
        self.cookie_cstk_var = StringVar(value="")
        self.cookie_login_var = StringVar(value="")
        self.cookie_sess_var = StringVar(value="")
        self._load_cookies()

        self._build()
        self._refresh_uploader_fields()

    def _build(self):
        self.root.title("youdaonote-pull 配置")
        self.root.geometry("820x700")
        self.root.minsize(700, 600)

        # 创建主框架
        main_frame = ttk.Frame(self.root)
        main_frame.pack(fill="both", expand=True)

        # 创建 Canvas 和滚动条
        self.canvas = Canvas(main_frame)
        scrollbar = ttk.Scrollbar(main_frame, orient="vertical", command=self.canvas.yview)
        self.scrollable_frame = ttk.Frame(self.canvas)

        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        )

        self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        self.canvas.configure(yscrollcommand=scrollbar.set)

        # 绑定鼠标滚轮
        self.canvas.bind_all("<MouseWheel>", self._on_mousewheel)

        scrollbar.pack(side="right", fill="y")
        self.canvas.pack(side="left", fill="both", expand=True)

        # 在 scrollable_frame 中构建 UI
        self._build_form()

    def _on_mousewheel(self, event):
        self.canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")

    def _build_form(self):
        frame = self.scrollable_frame
        frame.columnconfigure(1, weight=1)
        frame.columnconfigure(2, weight=1)

        current_row = 0

        ttk.Label(frame, text="配置文件").grid(row=current_row, column=0, sticky="w", padx=12, pady=(12, 6))
        ttk.Label(frame, text=self.config_path).grid(row=current_row, column=1, columnspan=3, sticky="w", padx=12, pady=(12, 6))
        current_row += 1

        ttk.Separator(frame).grid(row=current_row, column=0, columnspan=4, sticky="ew", padx=12, pady=8)
        current_row += 1

        # 有道云笔记登录 Cookies
        ttk.Label(frame, text="有道云笔记登录 Cookies", font=("", 10, "bold")).grid(
            row=current_row, column=0, columnspan=4, sticky="w", padx=12, pady=(0, 6)
        )
        current_row += 1

        current_row = self._add_entry_row(frame, current_row, "YNOTE_CSTK", self.cookie_cstk_var)
        current_row = self._add_entry_row(frame, current_row, "YNOTE_LOGIN", self.cookie_login_var)
        current_row = self._add_entry_row(frame, current_row, "YNOTE_SESS", self.cookie_sess_var)

        # Cookie 操作按钮
        cookie_btn_frame = ttk.Frame(frame)
        cookie_btn_frame.grid(row=current_row, column=0, columnspan=4, sticky="w", padx=12, pady=(6, 6))
        ttk.Button(cookie_btn_frame, text="从浏览器 Cookie 字符串导入", command=self._import_from_cookie_string).pack(side="left", padx=(0, 8))
        ttk.Button(cookie_btn_frame, text="测试 Cookie", command=self._test_cookie).pack(side="left", padx=(0, 8))
        current_row += 1

        ttk.Label(
            frame,
            text="从浏览器开发者工具中复制 Cookie 值，或点击上方按钮粘贴完整 Cookie 字符串",
            foreground="#666666",
        ).grid(row=current_row, column=0, columnspan=4, sticky="w", padx=12, pady=(0, 6))
        current_row += 1

        ttk.Separator(frame).grid(row=current_row, column=0, columnspan=4, sticky="ew", padx=12, pady=8)
        current_row += 1

        current_row = self._add_entry_row(
            frame,
            current_row,
            "导出目录",
            self.local_dir_var,
            button_text="选择目录",
            button_command=self._choose_local_dir,
        )
        current_row = self._add_entry_row(frame, current_row, "有道目录", self.ydnote_dir_var)

        ttk.Checkbutton(
            frame,
            text="Markdown 内图片/附件使用相对路径",
            variable=self.is_relative_path_var,
        ).grid(row=current_row, column=0, columnspan=4, sticky="w", padx=12, pady=6)
        current_row += 1

        ttk.Separator(frame).grid(row=current_row, column=0, columnspan=4, sticky="ew", padx=12, pady=8)
        current_row += 1

        ttk.Label(frame, text="图片处理").grid(row=current_row, column=0, sticky="w", padx=12, pady=(0, 6))
        uploader_frame = ttk.Frame(frame)
        uploader_frame.grid(row=current_row, column=1, columnspan=3, sticky="w", padx=12, pady=(0, 6))
        for value, text in (
            ("local", "仅下载到本地"),
            ("smms", "上传到 SM.MS"),
            ("aliyun_oss", "上传到阿里云 OSS"),
        ):
            ttk.Radiobutton(
                uploader_frame,
                text=text,
                value=value,
                variable=self.image_uploader_var,
                command=self._refresh_uploader_fields,
            ).pack(side="left", padx=(0, 16))
        current_row += 1

        self.smms_row = current_row
        current_row = self._add_entry_row(frame, current_row, "SM.MS Token", self.smms_secret_token_var, show="*")

        ttk.Label(frame, text="阿里云 OSS").grid(row=current_row, column=0, sticky="w", padx=12, pady=(6, 6))
        current_row += 1
        self.oss_rows = []
        current_row = self._add_oss_row(frame, current_row, "Endpoint", self.oss_endpoint_var)
        current_row = self._add_oss_row(frame, current_row, "Bucket", self.oss_bucket_var)
        current_row = self._add_oss_row(frame, current_row, "AccessKeyId", self.oss_access_key_id_var)
        current_row = self._add_oss_row(frame, current_row, "AccessKeySecret", self.oss_access_key_secret_var, show="*")
        current_row = self._add_oss_row(frame, current_row, "上传目录", self.oss_path_var)
        current_row = self._add_oss_row(frame, current_row, "自定义域名", self.oss_custom_domain_var)

        self.oss_https_row = current_row
        ttk.Checkbutton(
            frame,
            text="阿里云 OSS 上传与访问优先使用 HTTPS",
            variable=self.oss_use_https_var,
        ).grid(row=current_row, column=0, columnspan=4, sticky="w", padx=12, pady=6)
        current_row += 1

        ttk.Separator(frame).grid(row=current_row, column=0, columnspan=4, sticky="ew", padx=12, pady=8)
        current_row += 1

        ttk.Label(frame, text="PicGo").grid(row=current_row, column=0, sticky="w", padx=12, pady=(0, 6))
        ttk.Entry(frame, textvariable=self.picgo_config_path_var).grid(
            row=current_row, column=1, columnspan=2, sticky="ew", padx=12, pady=(0, 6)
        )
        ttk.Button(frame, text="读取默认配置", command=self._import_default_picgo).grid(
            row=current_row, column=3, sticky="ew", padx=12, pady=(0, 6)
        )
        current_row += 1

        ttk.Label(frame, text="").grid(row=current_row, column=0, padx=12, pady=0)
        ttk.Button(frame, text="选择 PicGo 配置文件", command=self._choose_picgo_config).grid(
            row=current_row, column=1, sticky="w", padx=12, pady=(0, 6)
        )
        current_row += 1

        ttk.Label(
            frame,
            text="支持直接导入 PicGo 的 picBed.smms 和 picBed.aliyun 配置。",
        ).grid(row=current_row, column=0, columnspan=4, sticky="w", padx=12, pady=(0, 8))
        current_row += 1

        ttk.Separator(frame).grid(row=current_row, column=0, columnspan=4, sticky="ew", padx=12, pady=8)
        current_row += 1

        ttk.Label(frame, textvariable=self.status_var, foreground="#555555").grid(
            row=current_row, column=0, columnspan=4, sticky="w", padx=12, pady=(0, 10)
        )
        current_row += 1

        # 底部按钮
        button_frame = ttk.Frame(frame)
        button_frame.grid(row=current_row, column=0, columnspan=4, sticky="e", padx=12, pady=(0, 12))
        ttk.Button(button_frame, text="测试 OSS", command=self._test_oss_connection).pack(side="left", padx=(0, 8))
        ttk.Button(button_frame, text="保存配置", command=self._save).pack(side="left", padx=(0, 8))
        ttk.Button(button_frame, text="运行导出", command=self._run_pull).pack(side="left", padx=(0, 8))
        ttk.Button(button_frame, text="保存并关闭", command=self._save_and_close).pack(side="left")

    def _add_entry_row(self, frame, row, label, variable, button_text=None, button_command=None, show=None):
        ttk.Label(frame, text=label).grid(row=row, column=0, sticky="w", padx=12, pady=6)
        entry = ttk.Entry(frame, textvariable=variable, show=show)
        entry.grid(row=row, column=1, columnspan=2, sticky="ew", padx=12, pady=6)
        if button_text and button_command:
            ttk.Button(frame, text=button_text, command=button_command).grid(
                row=row, column=3, sticky="ew", padx=12, pady=6
            )
        return row + 1

    def _add_oss_row(self, frame, row, label, variable, show=None):
        ttk.Label(frame, text=label).grid(row=row, column=0, sticky="w", padx=12, pady=6)
        entry = ttk.Entry(frame, textvariable=variable, show=show)
        entry.grid(row=row, column=1, columnspan=3, sticky="ew", padx=12, pady=6)
        self.oss_rows.append((row, entry))
        return row + 1

    def _choose_local_dir(self):
        selected = filedialog.askdirectory(initialdir=self.local_dir_var.get() or os.getcwd())
        if selected:
            self.local_dir_var.set(selected.replace("\\", "/"))

    def _choose_picgo_config(self):
        selected = filedialog.askopenfilename(
            initialdir=os.path.dirname(self.picgo_config_path_var.get()) if self.picgo_config_path_var.get() else os.getcwd(),
            filetypes=(("JSON 文件", "*.json"), ("所有文件", "*.*")),
        )
        if not selected:
            return
        self.picgo_config_path_var.set(selected)
        self._import_picgo(selected)

    def _import_default_picgo(self):
        self._import_picgo(self.picgo_config_path_var.get().strip() or None)

    def _import_picgo(self, picgo_config_path=None):
        imported, error_msg = import_config_from_picgo(picgo_config_path)
        if error_msg:
            self.status_var.set(error_msg)
            messagebox.showerror("读取 PicGo 失败", error_msg)
            return
        self.config = update_config_from_dict(self.config, imported)
        self._set_form_values(self.config)
        self.status_var.set("已导入 PicGo 配置")
        messagebox.showinfo("导入成功", "已导入 PicGo 配置")

    def _set_form_values(self, config: AppConfig):
        self.local_dir_var.set(config.local_dir)
        self.ydnote_dir_var.set(config.ydnote_dir)
        self.is_relative_path_var.set(config.is_relative_path)
        self.image_uploader_var.set(config.image_uploader)
        self.smms_secret_token_var.set(config.smms_secret_token)
        self.picgo_config_path_var.set(config.picgo_config_path)
        self.oss_endpoint_var.set(config.aliyun_oss.endpoint)
        self.oss_bucket_var.set(config.aliyun_oss.bucket)
        self.oss_access_key_id_var.set(config.aliyun_oss.access_key_id)
        self.oss_access_key_secret_var.set(config.aliyun_oss.access_key_secret)
        self.oss_path_var.set(config.aliyun_oss.path)
        self.oss_custom_domain_var.set(config.aliyun_oss.custom_domain)
        self.oss_use_https_var.set(config.aliyun_oss.use_https)
        self._refresh_uploader_fields()

    def _build_config(self) -> AppConfig:
        config_data = {
            "local_dir": self.local_dir_var.get().strip(),
            "ydnote_dir": self.ydnote_dir_var.get().strip(),
            "smms_secret_token": self.smms_secret_token_var.get().strip(),
            "is_relative_path": self.is_relative_path_var.get(),
            "image_uploader": self.image_uploader_var.get().strip() or "local",
            "picgo_config_path": self.picgo_config_path_var.get().strip(),
            "aliyun_oss": {
                "endpoint": self.oss_endpoint_var.get().strip(),
                "bucket": self.oss_bucket_var.get().strip(),
                "access_key_id": self.oss_access_key_id_var.get().strip(),
                "access_key_secret": self.oss_access_key_secret_var.get().strip(),
                "path": self.oss_path_var.get().strip(),
                "custom_domain": self.oss_custom_domain_var.get().strip(),
                "use_https": self.oss_use_https_var.get(),
            },
        }
        return AppConfig.from_dict(config_data)

    def _refresh_uploader_fields(self):
        smms_enabled = self.image_uploader_var.get() == "smms"
        oss_enabled = self.image_uploader_var.get() == "aliyun_oss"
        self._set_row_state(self.smms_row, smms_enabled)
        for row, _ in self.oss_rows:
            self._set_row_state(row, oss_enabled)
        self._set_row_state(self.oss_https_row, oss_enabled)

    def _set_row_state(self, row, enabled):
        state = "normal" if enabled else "disabled"
        for child in self.scrollable_frame.grid_slaves(row=row):
            try:
                child.configure(state=state)
            except Exception:
                pass

    def _save(self):
        try:
            self.config = self._build_config()
            save_config(self.config, self.config_path)
            self._save_cookies()
        except Exception as error:
            self.status_var.set("保存失败：{}".format(error))
            messagebox.showerror("保存失败", str(error))
            return
        self.status_var.set("配置已保存")
        messagebox.showinfo("保存成功", "配置已保存到\n{}".format(self.config_path))

    def _save_and_close(self):
        self._save()
        if self.status_var.get() == "配置已保存":
            self.root.destroy()

    def _load_cookies(self):
        """从 cookies.json 加载 cookies"""
        import json
        cookies_path = os.path.join(os.path.dirname(self.config_path), "cookies.json")
        if not os.path.exists(cookies_path):
            return

        try:
            with open(cookies_path, "r", encoding="utf-8") as f:
                data = json.load(f)
                cookies = data.get("cookies", [])
                for cookie in cookies:
                    if len(cookie) >= 2:
                        name, value = cookie[0], cookie[1]
                        if name == "YNOTE_CSTK":
                            self.cookie_cstk_var.set(value)
                        elif name == "YNOTE_LOGIN":
                            self.cookie_login_var.set(value)
                        elif name == "YNOTE_SESS":
                            self.cookie_sess_var.set(value)
        except Exception:
            pass

    def _save_cookies(self):
        """保存 cookies 到 cookies.json"""
        import json
        cstk = self.cookie_cstk_var.get().strip()
        login = self.cookie_login_var.get().strip()
        sess = self.cookie_sess_var.get().strip()

        if not any([cstk, login, sess]):
            return

        cookies_data = {
            "cookies": [
                ["YNOTE_CSTK", cstk, ".note.youdao.com", "/"],
                ["YNOTE_LOGIN", login, ".note.youdao.com", "/"],
                ["YNOTE_SESS", sess, ".note.youdao.com", "/"],
            ]
        }

        cookies_path = os.path.join(os.path.dirname(self.config_path), "cookies.json")
        try:
            with open(cookies_path, "w", encoding="utf-8") as f:
                json.dump(cookies_data, f, ensure_ascii=False, indent=4)
        except Exception as error:
            raise Exception("保存 cookies 失败：{}".format(error))

    def _import_from_cookie_string(self):
        """从浏览器 Cookie 字符串导入"""
        cookie_string = simpledialog.askstring(
            "导入 Cookie",
            "请粘贴从浏览器开发者工具复制的完整 Cookie 字符串：\n\n"
            "1. 打开有道云笔记网页并登录\n"
            "2. 按 F12 打开开发者工具\n"
            "3. 切换到 Network 标签\n"
            "4. 刷新页面，找到第一个请求\n"
            "5. 在 Headers 中找到 Cookie，复制完整值",
            parent=self.root,
        )

        if not cookie_string:
            return

        cookie_string = cookie_string.strip()
        if not cookie_string:
            messagebox.showwarning("输入为空", "请输入有效的 Cookie 字符串")
            return

        # 解析 Cookie 字符串
        cookies = {}
        for item in cookie_string.split(";"):
            item = item.strip()
            if "=" in item:
                key, value = item.split("=", 1)
                cookies[key.strip()] = value.strip()

        # 提取需要的 Cookie
        cstk = cookies.get("YNOTE_CSTK", "")
        login = cookies.get("YNOTE_LOGIN", "")
        sess = cookies.get("YNOTE_SESS", "")

        if not any([cstk, login, sess]):
            messagebox.showerror(
                "解析失败",
                "未能从 Cookie 字符串中找到 YNOTE_CSTK、YNOTE_LOGIN 或 YNOTE_SESS\n\n"
                "请确认：\n"
                "1. 已登录有道云笔记\n"
                "2. 复制的是完整的 Cookie 字符串\n"
                "3. Cookie 字符串包含 YNOTE_ 开头的字段",
            )
            return

        # 更新界面
        if cstk:
            self.cookie_cstk_var.set(cstk)
        if login:
            self.cookie_login_var.set(login)
        if sess:
            self.cookie_sess_var.set(sess)

        found_items = []
        if cstk:
            found_items.append("YNOTE_CSTK")
        if login:
            found_items.append("YNOTE_LOGIN")
        if sess:
            found_items.append("YNOTE_SESS")

        self.status_var.set("已导入 Cookie：{}".format(", ".join(found_items)))
        messagebox.showinfo(
            "导入成功",
            "已成功导入以下 Cookie：\n{}".format("\n".join(found_items)),
        )

    def _test_cookie(self):
        """测试 Cookie 是否有效"""
        cstk = self.cookie_cstk_var.get().strip()
        login = self.cookie_login_var.get().strip()
        sess = self.cookie_sess_var.get().strip()

        if not all([cstk, login, sess]):
            messagebox.showwarning("配置不完整", "请填写完整的 Cookie 信息（YNOTE_CSTK、YNOTE_LOGIN、YNOTE_SESS）")
            return

        self.status_var.set("正在测试 Cookie...")
        self.root.update()

        def test_in_thread():
            try:
                import requests

                # 创建 session 并设置 cookies
                session = requests.session()
                session.headers = {
                    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/100.0.4896.88 Safari/537.36",
                    "Accept": "*/*",
                    "Accept-Encoding": "gzip, deflate",
                    "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
                }

                # 设置 cookies
                session.cookies.set("YNOTE_CSTK", cstk, domain=".note.youdao.com", path="/")
                session.cookies.set("YNOTE_LOGIN", login, domain=".note.youdao.com", path="/")
                session.cookies.set("YNOTE_SESS", sess, domain=".note.youdao.com", path="/")

                # 调用获取根目录的 API 来验证 Cookie
                root_url = "https://note.youdao.com/yws/api/personal/file?method=getByPath&keyfrom=web&cstk={}".format(cstk)
                data = {"path": "/", "entire": "true", "purge": "false", "cstk": cstk}
                response = session.post(root_url, data=data)

                if response.status_code != 200:
                    error_msg = "HTTP 状态码：{}".format(response.status_code)
                    self.root.after(0, lambda msg=error_msg: self._show_cookie_test_error(msg))
                    return

                result = response.json()
                # 检查是否返回了有效的文件信息
                if "fileEntry" in result:
                    root_name = result["fileEntry"].get("name", "ROOT")
                    self.root.after(0, self._show_cookie_test_success)
                elif "errorCode" in result:
                    error_msg = "错误码：{}，{}".format(result.get("errorCode"), result.get("errorMessage", "Cookie 可能已过期"))
                    self.root.after(0, lambda msg=error_msg: self._show_cookie_test_error(msg))
                else:
                    error_msg = "未知响应：{}".format(str(result)[:200])
                    self.root.after(0, lambda msg=error_msg: self._show_cookie_test_error(msg))
            except Exception as e:
                error_msg = str(e)
                self.root.after(0, lambda msg=error_msg: self._show_cookie_test_error(msg))

        thread = threading.Thread(target=test_in_thread, daemon=True)
        thread.start()

    def _show_cookie_test_success(self):
        self.status_var.set("Cookie 测试成功")
        messagebox.showinfo("测试成功", "Cookie 验证成功！\n可以正常访问有道云笔记。")

    def _show_cookie_test_error(self, error_msg):
        self.status_var.set("Cookie 测试失败")
        messagebox.showerror("测试失败", "Cookie 验证失败：\n{}".format(error_msg))

    def _test_oss_connection(self):
        """测试阿里云 OSS 连接"""
        try:
            import oss2
        except ImportError:
            messagebox.showerror("缺少依赖", "请先安装 oss2：pip install oss2")
            return

        config = self._build_config()
        oss_cfg = config.aliyun_oss

        if not all([oss_cfg.endpoint, oss_cfg.bucket, oss_cfg.access_key_id, oss_cfg.access_key_secret]):
            messagebox.showwarning("配置不完整", "请先填写完整的阿里云 OSS 配置")
            return

        self.status_var.set("正在测试 OSS 连接...")
        self.root.update()

        def test_in_thread():
            try:
                from core.image import ImageUpload
                endpoint = ImageUpload._normalize_oss_endpoint(oss_cfg.endpoint, oss_cfg.use_https)
                auth = oss2.Auth(oss_cfg.access_key_id, oss_cfg.access_key_secret)
                bucket = oss2.Bucket(auth, endpoint, oss_cfg.bucket)

                # 测试上传一个小文件
                test_content = b"youdaonote-pull test"
                test_key = "test/connection_test.txt"
                if oss_cfg.path:
                    test_key = "{}/{}".format(oss_cfg.path.strip("/"), "connection_test.txt")

                bucket.put_object(test_key, test_content)

                # 测试读取
                result = bucket.get_object(test_key)
                if result.read() == test_content:
                    # 删除测试文件
                    bucket.delete_object(test_key)
                    self.root.after(0, self._show_test_success)
                else:
                    error_msg = "读取测试文件失败"
                    self.root.after(0, lambda msg=error_msg: self._show_test_error(msg))
            except Exception as e:
                error_msg = str(e)
                self.root.after(0, lambda msg=error_msg: self._show_test_error(msg))

        thread = threading.Thread(target=test_in_thread, daemon=True)
        thread.start()

    def _show_test_success(self):
        self.status_var.set("OSS 连接测试成功")
        messagebox.showinfo("测试成功", "阿里云 OSS 连接测试成功！\n可以正常上传和读取文件。")

    def _show_test_error(self, error_msg):
        self.status_var.set("OSS 连接测试失败")
        messagebox.showerror("测试失败", "阿里云 OSS 连接测试失败：\n{}".format(error_msg))

    def _run_pull(self):
        """运行导出"""
        # 先保存配置
        try:
            self.config = self._build_config()
            save_config(self.config, self.config_path)
            self.status_var.set("配置已保存，准备运行...")
        except Exception as error:
            messagebox.showerror("保存失败", "保存配置失败：{}".format(error))
            return

        # 确认是否运行
        if not messagebox.askyesno("确认运行", "即将开始导出有道云笔记，是否继续？"):
            self.status_var.set("已取消运行")
            return

        self.status_var.set("正在运行导出，请查看控制台输出...")
        self.root.update()

        def run_in_thread():
            try:
                from pull import run_pull
                exit_code = run_pull(self.config_path)
                if exit_code == 0:
                    self.root.after(0, self._show_run_success)
                else:
                    error_msg = "导出过程返回错误代码：{}".format(exit_code)
                    self.root.after(0, lambda msg=error_msg: self._show_run_error(msg))
            except Exception as e:
                error_msg = str(e)
                self.root.after(0, lambda msg=error_msg: self._show_run_error(msg))

        thread = threading.Thread(target=run_in_thread, daemon=True)
        thread.start()

    def _show_run_success(self):
        self.status_var.set("导出完成")
        messagebox.showinfo("导出完成", "有道云笔记导出完成！\n请查看导出目录。")

    def _show_run_error(self, error_msg):
        self.status_var.set("导出失败")
        messagebox.showerror("导出失败", "导出过程出错：\n{}".format(error_msg))


def open_config_ui(config_path=None) -> int:
    target_config_path = os.path.abspath(config_path or default_config_path())
    initial_message = ""
    if os.path.exists(target_config_path):
        config, error_msg = load_config(target_config_path)
        if error_msg:
            config = AppConfig()
            initial_message = error_msg
        else:
            initial_message = "已加载现有配置"
    else:
        config = AppConfig()
        initial_message = "未找到配置文件，将按默认值创建"

    root = Tk()
    root.columnconfigure(1, weight=1)
    root.columnconfigure(2, weight=1)
    window = ConfigWindow(root, config, target_config_path, initial_message)
    root.mainloop()
    return 0
