
# -*- coding: utf-8 -*-
import subprocess
import re
import platform
import ctypes
import sys
import os
import time
import locale
import winreg

class WindowsActivationManager:
    def __init__(self):
        self.admin = self.is_admin()
        self.running = True
        self.setup_encoding()
        self.show_disclaimer()
        
    def setup_encoding(self):
        """设置编码以解决乱码问题"""
        try:
            os.system('chcp 65001 > nul')
            if hasattr(sys.stdout, 'reconfigure'):
                sys.stdout.reconfigure(encoding='utf-8')
        except:
            pass
        self.encoding = locale.getpreferredencoding() or 'gbk'
        
    def show_disclaimer(self):
        """显示免责声明"""
        self.clear_screen()
        print("=" * 70)
        print("                   免责声明")
        print("=" * 70)
        print()
        print("重要提示：")
        print("1. 本程序仅供学习和研究目的使用")
        print("2. 请确保您拥有合法的Windows许可证")
        print("3. 使用KMS激活仅适用于拥有合法批量许可证的环境")
        print("4. 非法激活Windows可能违反法律法规")
        print("5. 使用者应对其行为承担全部法律责任")
        print("6. 开发者不承担任何因滥用本程序导致的法律责任")
        print()
        print("继续使用本程序即表示您已阅读并同意以上条款")
        print()
        
        try:
            input("按Enter键接受免责声明并继续...")
        except:
            pass
    
    def is_admin(self):
        """检查是否以管理员权限运行"""
        try:
            return ctypes.windll.shell32.IsUserAnAdmin()
        except:
            return False
    
    def clear_screen(self):
        """清屏"""
        os.system('cls' if os.name == 'nt' else 'clear')
    
    def print_header(self):
        """打印标题"""
        self.clear_screen()
        print("=" * 60)
        print("       Windows Activation Management Tool")
        print("=" * 60)
        print()
        
        if self.admin:
            print("[√] 当前以管理员权限运行")
        else:
            print("[!] 当前未以管理员权限运行，部分功能可能受限")
        print()
    
    def get_system_tool_path(self, tool_name):
        """获取系统工具完整路径"""
        windir = os.environ.get('WINDIR', 'C:\\Windows')
        possible_paths = [
            os.path.join(windir, 'System32', tool_name),
            os.path.join(windir, 'SysWOW64', tool_name),
            os.path.join(windir, 'system32', tool_name),
        ]
        
        for path in possible_paths:
            if os.path.exists(path):
                return path
        return tool_name
    
    def run_command(self, cmd, show_output=True):
        """执行命令并返回输出"""
        try:
            result = subprocess.run(
                cmd, 
                capture_output=True, 
                text=True, 
                shell=True, 
                encoding=self.encoding,
                errors='replace'
            )
            output = result.stdout
            if show_output and output.strip():
                for line in output.split('\n'):
                    if line.strip():
                        print(f"  {line.strip()}")
            return output
        except Exception as e:
            error_msg = f"执行命令出错: {str(e)}"
            if show_output:
                print(f"  [错误] {error_msg}")
            return error_msg
    
    def run_slmgr_command(self, args, show_output=True):
        """运行slmgr命令"""
        slmgr_path = self.get_system_tool_path('slmgr.vbs')
        cscript_path = self.get_system_tool_path('cscript.exe')
        
        cmd = f'"{cscript_path}" //nologo "{slmgr_path}" {args}'
        return self.run_command(cmd, show_output)
    
    def run_wmic_command(self, args, show_output=True):
        """运行WMIC命令"""
        wmic_path = self.get_system_tool_path('wmic.exe')
        cmd = f'"{wmic_path}" {args}'
        return self.run_command(cmd, show_output)
    
    def run_powershell_command(self, args, show_output=True):
        """运行PowerShell命令"""
        powershell_path = self.get_system_tool_path('powershell.exe')
        cmd = f'"{powershell_path}" -Command "{args}"'
        return self.run_command(cmd, show_output)
    
    def check_activation_status(self):
        """检查激活状态"""
        print("[激活状态检测]")
        
        # 使用slmgr命令检测
        print("1. 使用slmgr命令检测:")
        self.run_slmgr_command("/dli")
        
        print("\n2. 许可证详细信息:")
        self.run_slmgr_command("/dlv")
        
        print("\n3. 激活过期时间:")
        self.run_slmgr_command("/xpr")
        
        # 使用WMIC获取基本信息
        print("\n4. 系统信息:")
        try:
            output = self.run_wmic_command('os get caption,version /format:value', False)
            if output:
                for line in output.split('\n'):
                    if '=' in line:
                        key, value = line.split('=', 1)
                        print(f"  {key.strip()}: {value.strip()}")
        except:
            pass
        
        print()
    
    def get_backup_product_key(self):
        """从注册表获取备份的产品密钥"""
        try:
            key_path = r"SOFTWARE\Microsoft\Windows NT\CurrentVersion\SoftwareProtectionPlatform"
            with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, key_path) as key:
                try:
                    backup_key, _ = winreg.QueryValueEx(key, "BackupProductKeyDefault")
                    if backup_key and len(backup_key.strip()) > 10:
                        return backup_key.strip()
                except FileNotFoundError:
                    pass
        except Exception as e:
            print(f"  读取BackupProductKeyDefault失败: {e}")
        
        return None

    def get_registry_product_info(self):
        """从注册表获取产品信息"""
        product_info = {}
        
        try:
            # 主要注册表路径
            key_path = r"SOFTWARE\Microsoft\Windows NT\CurrentVersion"
            with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, key_path) as key:
                try:
                    product_name, _ = winreg.QueryValueEx(key, "ProductName")
                    product_info['ProductName'] = product_name
                except FileNotFoundError:
                    pass
                    
                try:
                    edition_id, _ = winreg.QueryValueEx(key, "EditionID")
                    product_info['EditionID'] = edition_id
                except FileNotFoundError:
                    pass
                    
                try:
                    product_id, _ = winreg.QueryValueEx(key, "ProductId")
                    product_info['ProductId'] = product_id
                except FileNotFoundError:
                    pass
                    
                try:
                    installation_type, _ = winreg.QueryValueEx(key, "InstallationType")
                    product_info['InstallationType'] = installation_type
                except FileNotFoundError:
                    pass
        except Exception as e:
            print(f"  读取产品信息失败: {e}")
        
        return product_info

    def get_oem_product_key(self):
        """获取OEM产品密钥"""
        print("\n6. OEM产品密钥查询:")
        
        # 方法1: 使用PowerShell从BIOS中提取OEM密钥
        print("  方法1: 从BIOS中提取OEM密钥:")
        try:
            ps_cmd = '(Get-WmiObject -query "select * from SoftwareLicensingService").OA3xOriginalProductKey'
            output = self.run_powershell_command(ps_cmd, False)
            if output and len(output.strip()) > 10:
                oem_key = output.strip()
                print(f"    OEM产品密钥: {oem_key}")
                return oem_key
            else:
                print("    未找到OEM产品密钥")
        except Exception as e:
            print(f"    PowerShell查询失败: {e}")
        
        # 方法2: 尝试从注册表获取OEM密钥
        print("  方法2: 注册表查询:")
        oem_registry_paths = [
            r"SOFTWARE\Microsoft\Windows NT\CurrentVersion",
            r"SOFTWARE\Microsoft\Windows\CurrentVersion\Setup\OOBE",
            r"SOFTWARE\Microsoft\Windows NT\CurrentVersion\SoftwareProtectionPlatform",
        ]
        
        for path in oem_registry_paths:
            try:
                with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, path) as key:
                    try:
                        value, _ = winreg.QueryValueEx(key, "ProductKey")
                        if value and len(str(value)) > 10:
                            print(f"    注册表路径 {path}: {value}")
                            return value
                    except FileNotFoundError:
                        pass
            except Exception as e:
                pass
        
        # 方法3: 使用WMIC查询
        print("  方法3: WMIC查询:")
        try:
            output = self.run_wmic_command('path softwarelicensingservice get OA3xOriginalProductKey /format:value', False)
            if output and 'OA3xOriginalProductKey' in output:
                for line in output.split('\n'):
                    if 'OA3xOriginalProductKey=' in line:
                        oem_key = line.split('=', 1)[1].strip()
                        if oem_key:
                            print(f"    OEM产品密钥: {oem_key}")
                            return oem_key
        except Exception as e:
            print(f"    WMIC查询失败: {e}")
        
        print("    未找到有效的OEM产品密钥")
        return None

    def show_installed_product_keys(self):
        """显示已安装的产品密钥 - 改进版本"""
        print("[已安装的产品密钥]")
        print()
        
        key_found = False
        
        # 方法1: 从SoftwareProtectionPlatform读取备份密钥
        print("1. 从注册表读取备份产品密钥:")
        backup_key = self.get_backup_product_key()
        if backup_key:
            print(f"  备份产品密钥: {backup_key}")
            key_found = True
        else:
            print("  未找到备份产品密钥")
        
        # 方法2: 使用slmgr命令获取信息
        print("\n2. 使用slmgr命令查询激活信息:")
        output = self.run_slmgr_command("/dli", False)
        
        # 解析slmgr输出
        lines = output.split('\n')
        license_status = "未知"
        for line in lines:
            line_lower = line.lower()
            if 'license status' in line_lower or '授权状态' in line:
                license_status = line.split(':')[-1].strip() if ':' in line else line
                print(f"  授权状态: {license_status}")
            elif 'partial product key' in line_lower or '部分产品密钥' in line:
                partial_key = line.split(':')[-1].strip() if ':' in line else line
                print(f"  部分产品密钥: {partial_key}")
                key_found = True
        
        # 方法3: 获取产品信息
        print("\n3. 产品信息:")
        product_info = self.get_registry_product_info()
        if product_info:
            for key, value in product_info.items():
                print(f"  {key}: {value}")
        
        # 方法4: 使用PowerShell获取更多信息
        print("\n4. 使用PowerShell查询:")
        try:
            # 查询激活状态
            ps_cmd = 'Get-CimInstance -ClassName SoftwareLicensingProduct | Where-Object {$_.PartialProductKey} | Select-Object Name, LicenseStatus, PartialProductKey'
            output = self.run_powershell_command(ps_cmd, False)
            if output and 'PartialProductKey' in output:
                lines = output.strip().split('\n')
                for line in lines:
                    if line.strip() and not line.startswith('Name') and not line.startswith('-'):
                        print(f"  {line.strip()}")
                        key_found = True
        except Exception as e:
            print(f"  PowerShell查询失败: {e}")
        
        # 方法5: 尝试读取其他可能的注册表位置
        print("\n5. 其他注册表位置查询:")
        try:
            registry_locations = [
                (r"SOFTWARE\Microsoft\Windows NT\CurrentVersion", "DigitalProductId"),
                (r"SOFTWARE\Microsoft\Windows\CurrentVersion\Setup\OOBE", "ProductKey"),
                (r"SOFTWARE\Microsoft\Windows NT\CurrentVersion", "ProductKey"),
            ]
            
            for path, value_name in registry_locations:
                try:
                    with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, path) as key:
                        try:
                            value, _ = winreg.QueryValueEx(key, value_name)
                            if value and isinstance(value, (str, bytes)) and len(str(value)) > 5:
                                if isinstance(value, bytes):
                                    print(f"  {path}\\{value_name}: [二进制数据，需要解码]")
                                else:
                                    # 对长密钥进行掩码处理
                                    if len(value) > 10:
                                        masked = value[:8] + "..." + value[-5:] if len(value) > 15 else value
                                        print(f"  {path}\\{value_name}: {masked}")
                                    else:
                                        print(f"  {path}\\{value_name}: {value}")
                                key_found = True
                        except FileNotFoundError:
                            pass
                except Exception:
                    pass
        except Exception as e:
            print(f"  其他注册表查询失败: {e}")
        
        # 方法6: 获取OEM产品密钥
        oem_key = self.get_oem_product_key()
        if oem_key:
            key_found = True
        
        if not key_found:
            print("\n[提示] 未找到完整的产品密钥信息")
            print("可能的原因:")
            print("  - 系统使用数字许可证激活而非产品密钥")
            print("  - 产品密钥信息被系统保护")
            print("  - 当前权限不足")
            print("  - OEM设备的密钥嵌入在BIOS中")
        
        print("\n[说明]")
        print("  - 备份产品密钥是系统存储的用于重新激活的密钥")
        print("  - 部分产品密钥用于验证激活状态")
        print("  - 数字许可证激活可能不会显示产品密钥")
        print("  - OEM产品密钥是预装在设备中的原始密钥")
        print()

    def get_oem_info(self):
        """查询OEM信息"""
        print("[OEM信息查询]")
        print()
        
        # 方法1: 通过WMIC获取OEM信息
        print("1. 通过WMIC获取制造商信息:")
        try:
            output = self.run_wmic_command('computersystem get manufacturer,model /format:value', False)
            if output:
                for line in output.split('\n'):
                    if '=' in line:
                        key, value = line.split('=', 1)
                        if value.strip():
                            print(f"  {key.strip()}: {value.strip()}")
        except Exception as e:
            print(f"  WMIC查询失败: {e}")
        
        # 方法2: 查询注册表中的OEM信息
        print("\n2. 注册表中的OEM信息:")
        oem_keys = [
            (r"SOFTWARE\Microsoft\Windows\CurrentVersion\OEMInformation", "Manufacturer"),
            (r"SOFTWARE\Microsoft\Windows\CurrentVersion\OEMInformation", "Model"),
            (r"SOFTWARE\Microsoft\Windows\CurrentVersion\OEMInformation", "SupportHours"),
            (r"SOFTWARE\Microsoft\Windows\CurrentVersion\OEMInformation", "SupportPhone"),
            (r"SOFTWARE\Microsoft\Windows\CurrentVersion\OEMInformation", "SupportURL"),
            (r"SOFTWARE\Microsoft\Windows\CurrentVersion\OEMInformation", "Logo"),
        ]
        
        oem_found = False
        for path, value_name in oem_keys:
            try:
                with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, path) as key:
                    try:
                        value, value_type = winreg.QueryValueEx(key, value_name)
                        if value:
                            print(f"  {value_name}: {value}")
                            oem_found = True
                    except FileNotFoundError:
                        pass
            except Exception:
                pass
        
        if not oem_found:
            print("  未找到OEM信息")
        
        # 方法3: 查询BIOS信息
        print("\n3. BIOS信息:")
        try:
            output = self.run_wmic_command('bios get manufacturer,serialnumber,version /format:value', False)
            if output:
                for line in output.split('\n'):
                    if '=' in line:
                        key, value = line.split('=', 1)
                        if value.strip():
                            print(f"  {key.strip()}: {value.strip()}")
        except Exception as e:
            print(f"  BIOS查询失败: {e}")
        
        # 方法4: 获取OEM产品密钥
        print("\n4. OEM产品密钥:")
        oem_key = self.get_oem_product_key()
        if oem_key:
            print(f"  OEM产品密钥: {oem_key}")
        else:
            print("  未找到OEM产品密钥")
        
        print()

    def validate_product_key(self, key):
        """验证产品密钥格式"""
        # 移除可能的分隔符并验证
        clean_key = key.replace('-', '').replace(' ', '').upper()
        if len(clean_key) != 25:
            return False
        
        # 更宽松的验证 - 允许所有大写字母和数字
        # 但排除容易混淆的字符 (0, O, 1, I, L 等)
        allowed_chars = set('ABCDEFGHJKLMNPQRSTUVWXYZ23456789')
        return all(c in allowed_chars for c in clean_key)

    def install_product_key(self):
        """安装产品密钥"""
        print("[安装产品密钥]")
        
        if not self.admin:
            print("[错误] 此操作需要管理员权限，请以管理员身份重新运行程序")
            print()
            return False
        
        print("请输入有效的Windows产品密钥 (格式: XXXXX-XXXXX-XXXXX-XXXXX-XXXXX)")
        print("支持的版本: Windows 10/11")
        print("或直接按Enter取消操作")
        print()
        
        while True:
            try:
                product_key = input("产品密钥: ").strip()
                
                if not product_key:
                    print("取消安装")
                    return False
                
                # 标准化密钥格式
                product_key = product_key.upper().replace(' ', '-')
                    
                if self.validate_product_key(product_key):
                    break
                else:
                    print("密钥格式不正确，请重新输入")
                    print("正确格式示例: XXXXX-XXXXX-XXXXX-XXXXX-XXXXX")
                    print()
            except UnicodeDecodeError:
                print("输入编码错误，请重新输入")
            except Exception as e:
                print(f"输入错误: {str(e)}")
        
        print()
        print(f"将要安装的密钥: {product_key}")
        try:
            confirm = input("确认安装? (y/N): ").strip().lower()
        except:
            confirm = 'n'
        
        if confirm != 'y':
            print("取消安装")
            return False
        
        print()
        print("正在安装产品密钥...")
        result = self.run_slmgr_command(f"/ipk {product_key}")
        
        # 检查安装结果
        if "成功" in result or "successfully" in result.lower():
            print("[成功] 产品密钥安装成功")
            
            # 询问是否立即激活
            print()
            try:
                activate_now = input("是否立即尝试激活Windows? (y/N): ").strip().lower()
                if activate_now == 'y':
                    self.activate_windows()
            except:
                pass
                
            return True
        else:
            print(f"[错误] 产品密钥安装失败")
            print(f"详细错误: {result}")
            return False

    def activate_windows(self):
        """激活Windows"""
        print("[激活Windows]")
        
        if not self.admin:
            print("[错误] 此操作需要管理员权限，请以管理员身份重新运行程序")
            print()
            return False
        
        print("正在尝试激活Windows...")
        print()
        
        # 使用默认的Microsoft激活服务器
        result = self.run_slmgr_command("/ato")
        
        if "成功" in result or "successfully" in result.lower() or "activated" in result.lower():
            print("[成功] Windows激活成功")
            return True
        else:
            print("[错误] Windows激活失败")
            print("可能的原因:")
            print("  - 未安装有效的产品密钥")
            print("  - 网络连接问题")
            print("  - 激活服务器不可用")
            print("  - 产品密钥无效或已达到激活限制")
            return False

    def kms_activation(self):
        """KMS激活"""
        print("[KMS激活]")
        
        if not self.admin:
            print("[错误] 此操作需要管理员权限，请以管理员身份重新运行程序")
            print()
            return False
        
        print("警告: KMS激活仅适用于拥有合法批量许可证的环境")
        print("非法使用KMS激活可能违反软件许可协议")
        print()
        
        try:
            confirm = input("确认继续使用KMS激活? (y/N): ").strip().lower()
        except:
            confirm = 'n'
        
        if confirm != 'y':
            print("取消KMS激活")
            return False
        
        print()
        print("请输入KMS服务器地址 (例如: kms.example.com或者ip地址)")
        print("或使用公共KMS服务器 (直接按Enter使用默认127.0.0.1)")
        print()
        
        try:
            kms_server = input("KMS服务器地址: ").strip()
            if not kms_server:
                kms_server = "127.0.0.1"  # 示例服务器，实际使用时请替换
                print(f"使用默认KMS服务器: {kms_server}")
        except:
            print("输入错误，会重新定向到127.0.0.1")
            kms_server = "k127.0.0.1"
        
        print()
        print(f"正在设置KMS服务器: {kms_server}")
        
        # 设置KMS服务器
        result = self.run_slmgr_command(f"/skms {kms_server}")
        
        if "成功" in result or "successfully" in result.lower():
            print("[成功] KMS服务器设置成功")
            
            # 尝试激活
            print("正在尝试KMS激活...")
            activate_result = self.run_slmgr_command("/ato")
            
            if "成功" in activate_result or "successfully" in activate_result.lower():
                print("[成功] KMS激活成功")
                return True
            else:
                print("[错误] KMS激活失败")
                print("可能的原因:")
                print("  - KMS服务器不可用")
                print("  - 当前系统版本不支持KMS激活")
                print("  - 网络连接问题")
                return False
        else:
            print("[错误] KMS服务器设置失败")
            return False

    def show_reset_options(self):
        """显示重置选项"""
        print("[重置激活状态]")
        
        if not self.admin:
            print("[错误] 此操作需要管理员权限，请以管理员身份重新运行程序")
            print()
            return False
        
        print("警告: 重置激活状态将清除当前的激活信息")
        print("这可能导致Windows变为未激活状态")
        print()
        print("请选择重置选项:")
        print("1. 清除当前产品密钥")
        print("2. 重置授权状态")
        print("3. 强制重新激活")
        print("4. 取消")
        print()
        
        try:
            choice = input("请输入选项 (1-4): ").strip()
        except:
            return False
        
        if choice == '1':
            print()
            print("正在清除产品密钥...")
            result = self.run_slmgr_command("/upk")
            if "成功" in result or "successfully" in result.lower():
                print("[成功] 产品密钥已清除")
                return True
            else:
                print("[错误] 清除产品密钥失败")
                return False
        
        elif choice == '2':
            print()
            print("正在重置授权状态...")
            result = self.run_slmgr_command("/rearm")
            if "成功" in result or "successfully" in result.lower():
                print("[成功] 授权状态已重置")
                print("需要重新启动计算机才能完成重置")
                return True
            else:
                print("[错误] 重置授权状态失败")
                return False
        
        elif choice == '3':
            print()
            print("正在强制重新激活...")
            # 先清除密钥
            self.run_slmgr_command("/upk")
            # 然后重新激活
            result = self.run_slmgr_command("/ato")
            if "成功" in result or "successfully" in result.lower():
                print("[成功] 强制重新激活完成")
                return True
            else:
                print("[错误] 强制重新激活失败")
                return False
        
        elif choice == '4':
            print("取消重置操作")
            return False
        
        else:
            print("无效选项")
            return False

    def show_menu(self):
        """显示菜单"""
        print("请选择操作:")
        print("1. 检测激活状态")
        print("2. 显示产品密钥")
        print("3. 安装产品密钥")
        print("4. 激活Windows")
        print("5. KMS激活")
        print("6. 查询OEM信息")
        print("7. 重置激活状态")
        print("8. 退出程序")
        print()
    
    def wait_for_enter(self):
        """等待用户按Enter键"""
        print()
        try:
            input("按Enter键继续...")
        except:
            print("输入错误，继续执行...")
            time.sleep(2)
    
    def main_loop(self):
        """主循环"""
        while self.running:
            try:
                self.print_header()
                self.show_menu()
                
                choice = input("请输入选项 (1-8): ").strip()
                
                if choice == '1':
                    self.print_header()
                    self.check_activation_status()
                    self.wait_for_enter()
                elif choice == '2':
                    self.print_header()
                    self.show_installed_product_keys()
                    self.wait_for_enter()
                elif choice == '3':
                    self.print_header()
                    if self.install_product_key():
                        time.sleep(2)
                        self.print_header()
                        self.check_activation_status()
                    self.wait_for_enter()
                elif choice == '4':
                    self.print_header()
                    if self.activate_windows():
                        time.sleep(2)
                        self.print_header()
                        self.check_activation_status()
                    self.wait_for_enter()
                elif choice == '5':
                    self.print_header()
                    if self.kms_activation():
                        time.sleep(2)
                        self.print_header()
                        self.check_activation_status()
                    self.wait_for_enter()
                elif choice == '6':
                    self.print_header()
                    self.get_oem_info()
                    self.wait_for_enter()
                elif choice == '7':
                    self.print_header()
                    if self.show_reset_options():
                        time.sleep(2)
                        self.print_header()
                        self.check_activation_status()
                    self.wait_for_enter()
                elif choice == '8':
                    print("按Enter键自动退出")
                    self.running = False
                else:
                    print("无效选项，请重新输入")
                    time.sleep(1)
            except KeyboardInterrupt:
                print("\n\n程序被用户中断")
                self.running = False
            except Exception as e:
                print(f"\n程序执行出错: {str(e)}")
                self.wait_for_enter()

def main():
    """主函数"""
    try:
        manager = WindowsActivationManager()
        manager.main_loop()
    except Exception as e:
        print(f"程序执行出错: {str(e)}")
    finally:
        try:
            input("\n按Enter键退出...")
        except:
            pass

if __name__ == "__main__":
    main()