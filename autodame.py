import requests
import re
import json
import time
import random
from typing import Dict, Any


list_dzi_chuyen_nghiep = [
    "Bước 1: Fake Profile → Me",
    "Bước 2: Fake tên vào biệt danh (nếu không có avatar)",
    "Bước 3: Chọn dòng 'Giả mạo danh tính' → Lựa chọn 'Giả mạo tôi hoặc người tôi biết'",
    "Bước 4: Chọn dòng 'Nội dung không phù hợp' → Lựa chọn 'Spam hoặc gây hiểu lầm'",
    "Bước 5: Chọn dòng 'Vi phạm cộng đồng' → Lựa chọn 'Ngôn từ kích động thù địch'",
    "Bước 6: Đang xử lý các bài post (chủ yếu cắn post để die nhanh)",
    "Bước 7: Chọn dòng 'Giả mạo danh tính' → Lựa chọn 'Giả mạo tôi hoặc người tôi biết'"
]

list_dzi_clone = [
    "Bước 1: Fake Profile → Me",
    "Bước 2: Fake Profile người nổi tiếng → 'markzuckerberg'",
    "Bước 3: Fake Profile doanh nghiệp → 'meta for business'",
    "Bước 4: Chọn dòng 'Nội dung người lớn' → Lựa chọn 'Vi phạm nội dung 18+'",
    "Bước 5: Chọn dòng 'Giả mạo danh tính' → Lựa chọn 'Tài khoản giả mạo'",
    "Bước 6: Chọn dòng 'Spam hoặc lừa đảo' → Lựa chọn 'Lừa đảo tài chính'",
    "Bước 7: Chọn dòng 'Vi phạm cộng đồng' → Lựa chọn 'Bạo lực hoặc tổ chức nguy hiểm'",
    "Bước 8: Chọn dòng 'Nội dung sai sự thật' → Lựa chọn 'Tin giả hoặc gây hiểu lầm'",
    "Bước 9: Chọn dòng 'Quấy rối' → Lựa chọn 'Quấy rối hoặc bắt nạt'",
    "Bước 10: Đang kẹp clone (để dễ die hơn)",
    "Bước 11: Chọn dòng 'Hành vi đáng ngờ' → Lựa chọn 'Tài khoản spam'",
    "Bước 12: Chọn dòng 'Bán hàng trái phép' → Lựa chọn 'Bán hàng vi phạm chính sách'"
]

list_dzi_profile_thuong = [
    "Bước 1: Fake Profile → Me",
    "Bước 2: Fake Profile người nổi tiếng → 'markzuckerberg'",
    "Bước 3: Fake Profile doanh nghiệp → 'meta for business'",
    "Bước 4: Chọn dòng 'Nội dung người lớn' → Lựa chọn 'Vi phạm nội dung 18+'",
    "Bước 5: Chọn dòng 'Giả mạo danh tính' → Lựa chọn 'Tài khoản giả mạo'",
    "Bước 6: Chọn dòng 'Vi phạm cộng đồng' → Lựa chọn 'Ngôn từ kích động thù địch'",
    "Bước 7: Chọn dòng 'Spam hoặc lừa đảo' → Lựa chọn 'Lừa đảo tài chính'",
    "Bước 8: Chọn dòng 'Bạo lực' → Lựa chọn 'Nội dung bạo lực hoặc đồ máu'",
    "Bước 9: Chọn dòng 'Quấy rối' → Lựa chọn 'Quấy rối hoặc bắt nạt'",
    "Bước 10: Chọn dòng 'Vi phạm quyền riêng tư' → Lựa chọn 'Chia sẻ thông tin cá nhân'",
    "Bước 11: Đang xử lý các bài post: Report all dòng 'Fraud or Scam'",
    "Bước 12: Chọn dòng 'Hành vi đáng ngờ' → Lựa chọn 'Tài khoản spam'"
]


class FacebookManager:
    def __init__(self, cookie):
        self.cookie = cookie
        self.fb_dtsg = None
        self.jazoest = None
        self.uid = None
        self.user_info = None
        
        try:
            self.uid = self._extract_user_id()
            self._init_params()
            self.user_info = self._get_own_info()
        except Exception as e:
            print(f"❌ Lỗi khởi tạo: {str(e)}")
            exit()
    
    def _extract_user_id(self):
        try:
            c_user = re.search(r"c_user=(\d+)", self.cookie).group(1)
            return c_user
        except:
            raise Exception("Cookie không hợp lệ hoặc đã hết hạn")

    def _init_params(self):
        headers = {
            'Cookie': self.cookie,
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.9,vi;q=0.8',
            'Sec-Fetch-Dest': 'document',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'none',
            'Sec-Fetch-User': '?1',
            'Upgrade-Insecure-Requests': '1'
        }

        try:
            response = requests.get('https://www.facebook.com', headers=headers, timeout=15)
            fb_dtsg_match = re.search(r'"token":"(.*?)"', response.text)
            jazoest_match = re.search(r'jazoest=(\d+)', response.text)
            
            if jazoest_match:
                self.jazoest = jazoest_match.group(1)
            
            if not fb_dtsg_match:
                response = requests.get('https://mbasic.facebook.com', headers=headers, timeout=15)
                fb_dtsg_match = re.search(r'name="fb_dtsg" value="(.*?)"', response.text)
                
                if not fb_dtsg_match:
                    response = requests.get('https://m.facebook.com', headers=headers, timeout=15)
                    fb_dtsg_match = re.search(r'name="fb_dtsg" value="(.*?)"', response.text)
                
                if not jazoest_match:
                    jazoest_match = re.search(r'jazoest=(\d+)', response.text)
                    if jazoest_match:
                        self.jazoest = jazoest_match.group(1)

            if fb_dtsg_match:
                self.fb_dtsg = fb_dtsg_match.group(1)
            else:
                with open('debug_response.html', 'w', encoding='utf-8') as f:
                    f.write(response.text)
                raise Exception("Không lấy được fb_dtsg - Cookie có thể đã hết hạn")
            
            if not self.jazoest:
                raise Exception("Không lấy được jazoest - Cookie có thể đã hết hạn")

        except requests.Timeout:
            raise Exception("Timeout khi kết nối Facebook")
        except Exception as e:
            raise Exception(f"Lỗi khi khởi tạo: {str(e)}")

    def _get_own_info(self):
        return self.get_user_info(self.uid)

    def get_user_info(self, uid):
        try:
            form = {
                "ids[0]": uid,
                "fb_dtsg": self.fb_dtsg,
                "__a": 1,
                "__req": "1b",
                "__rev": "1015919737"
            }
            
            headers = {
                'Accept': '*/*',
                'Accept-Language': 'vi-VN,vi;q=0.9',
                'Content-Type': 'application/x-www-form-urlencoded',
                'Cookie': self.cookie,
                'Origin': 'https://www.facebook.com',
                'Referer': 'https://www.facebook.com/',
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }
            
            response = requests.post(
                "https://www.facebook.com/chat/user_info/",
                headers=headers,
                data=form,
                timeout=10
            )
            
            if response.status_code != 200:
                return {"error": f"Lỗi kết nối: {response.status_code}"}
            
            text_response = response.text
            if text_response.startswith("for (;;);"):
                text_response = text_response[9:]
            
            res_data = json.loads(text_response)
            
            if "error" in res_data:
                return {"error": res_data.get("error")}
            
            if "payload" in res_data and "profiles" in res_data["payload"]:
                return self._format_user_data(res_data["payload"]["profiles"])
            else:
                return {"error": f"Không tìm thấy thông tin"}
                
        except json.JSONDecodeError:
            return {"error": "Lỗi phân tích dữ liệu"}
        except requests.Timeout:
            return {"error": "Timeout"}
        except Exception as e:
            return {"error": str(e)}

    def _format_user_data(self, profiles):
        if not profiles:
            return {"error": "Không có dữ liệu"}
        
        first_profile_id = next(iter(profiles))
        profile = profiles[first_profile_id]
        
        return {
            "id": first_profile_id,
            "name": profile.get("name", ""),
            "url": profile.get("url", ""),
            "thumbSrc": profile.get("thumbSrc", ""),
            "gender": profile.get("gender", "")
        }

    def get_uid_from_link(self, link):
        url = "https://id.traodoisub.com/api.php"
        headers = {
            "accept": "application/json, text/javascript, */*; q=0.01",
            "content-type": "application/x-www-form-urlencoded; charset=UTF-8",
            "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        }
        data = {"link": link}
        
        try:
            response = requests.post(url, headers=headers, data=data, timeout=10)
            if response.status_code == 200:
                return response.json().get("id")
            return None
        except:
            return None

    def check_uid_status(self, uid):
        api_url = f"https://keyherlyswar.x10.mx/Apidocs/checkuid.php?uid={uid}"
        try:
            response = requests.get(api_url, timeout=5)
            if response.status_code == 200:
                data = response.json()
                if data.get("uid") == uid:
                    return data.get("status", "unknown")
            return "unknown"
        except:
            return "error"

    def display_login_info(self):
        print("\n" + "="*60)
        print("✅ ĐĂNG NHẬP THÀNH CÔNG")
        print("="*60)
        
        if self.user_info and "error" not in self.user_info:
            print(f"👤 Tên tài khoản: {self.user_info['name']}")
            print(f"🆔 UID: {self.user_info['id']}")
            print(f"🔗 Profile: {self.user_info['url']}")
        else:
            print(f"⚠️  Không lấy được thông tin tài khoản")
        
        print("="*60 + "\n")

    def process_with_steps(self, list_steps, target_uid, target_name):
        print("\n" + "="*60)
        print(f"🎯 MỤC TIÊU: {target_name} (UID: {target_uid})")
        print("="*60 + "\n")
        
        cycle = 1
        while True:
            print(f"\n🔄 Vòng lặp #{cycle}")
            print("-" * 60)
            
            for step in list_steps:
                print(f"⏳ {step}")
                time.sleep(random.uniform(0.8, 2.0))
            
            print(f"\n✅ Hoàn thành vòng lặp #{cycle}")
            
            status = self.check_uid_status(target_uid)
            
            if status == "die":
                print("\n" + "="*60)
                print(f"🎉 THÀNH CÔNG! Tài khoản {target_name} đã bị khóa")
                print("="*60)
                break
            else:
                print(f"📊 Trạng thái: Tài khoản vẫn đang hoạt động, tiếp tục...")
                time.sleep(random.uniform(2, 4))
                cycle += 1


def main():
    print("="*60)
    print("    FACEBOOK ACCOUNT MANAGER TOOL")
    print("="*60)
    
    print("\n📌 Nhập Cookie Facebook của bạn:")
    cookie = input("👉 Cookie: ").strip()
    
    if not cookie:
        print("❌ Cookie không được để trống!")
        return
    
    try:
        manager = FacebookManager(cookie)
        manager.display_login_info()
    except Exception as e:
        print(f"❌ Lỗi: {str(e)}")
        return
    
    while True:
        print("\n" + "="*60)
        print("CHỨC NĂNG")
        print("="*60)
        print("1. Dame tài khoản Chuyên Nghiệp")
        print("2. Dame tài khoản Clone")
        print("3. Dame Profile Bình Thường")
        print("4. Xem Hướng Dẫn & Ghi Chú")
        print("0. Thoát")
        print("="*60)
        
        choice = input("\n👉 Chọn chức năng: ").strip()
        
        if choice in ["1", "2", "3"]:
            print("\n📌 Nhập link Facebook cần xử lý:")
            link = input("👉 Link: ").strip()
            
            if not link:
                print("❌ Link không được để trống!")
                continue
            
            print("\n⏳ Đang lấy thông tin...")
            uid = manager.get_uid_from_link(link)
            
            if not uid:
                print("❌ Không lấy được UID từ link này!")
                continue
            
            user_info = manager.get_user_info(uid)
            
            if "error" in user_info:
                print(f"❌ {user_info['error']}")
                continue
            
            status = manager.check_uid_status(uid)
            
            print("\n" + "="*60)
            print("THÔNG TIN TÀI KHOẢN")
            print("="*60)
            print(f"👤 Tên: {user_info['name']}")
            print(f"🆔 UID: {user_info['id']}")
            print(f"🔗 Link: {user_info['url']}")
            
            if status == "live":
                print(f"📊 Trạng thái: ✅ Đang hoạt động")
            elif status == "die":
                print(f"📊 Trạng thái: ❌ Đã bị khóa")
                print("="*60)
                print("\n⚠️  Tài khoản này đã bị khóa, không cần xử lý!")
                continue
            else:
                print(f"📊 Trạng thái: ⚠️  Không xác định")
            
            print("="*60)
            
            confirm = input("\n⚠️  Xác nhận xử lý tài khoản này? (y/n): ").strip().lower()
            
            if confirm == 'y':
                if choice == "1":
                    manager.process_with_steps(list_dzi_chuyen_nghiep, uid, user_info['name'])
                elif choice == "2":
                    manager.process_with_steps(list_dzi_clone, uid, user_info['name'])
                elif choice == "3":
                    manager.process_with_steps(list_dzi_profile_thuong, uid, user_info['name'])
            else:
                print("❌ Đã hủy xử lý")
        
        elif choice == "4":
            print("\n" + "="*60)
            print("📖 HƯỚNG DẪN & GHI CHÚ")
            print("="*60)
            
            print("\n⭐️ NGUYÊN LIỆU CẦN CÓ")
            print("-" * 60)
            print("• Via Tick India/Nepal/Bangladesh (ưu tiên Nepal)")
            print("• Clone cổ K110 hoặc cổ hơn (hoặc clone thường)")
            print("• Tool đổi IP: HMA Pro")
            print("• Thời gian: 30-40 phút/acc")
            
            print("\n📝 BƯỚC 1: CHUẨN BỊ TÀI KHOẢN")
            print("-" * 60)
            print("• Chuẩn bị 1 con Via Tick India/Nepal/Bangladesh")
            print("• Chuẩn bị 1 con Clone cổ K12 (hoặc clone thường)")
            print("• Đảm bảo cả 2 acc đều hoạt động tốt")
            
            print("\n🎨 BƯỚC 2: FAKE PROFILE CƠ BẢN")
            print("-" * 60)
            print("• Fake avatar lên ảnh bìa")
            print("• Fake tên vào biệt danh")
            print("• Fake tiểu sử (nếu có)")
            print("• Làm cho profile trông tự nhiên nhất có thể")
            
            print("\n🌍 BƯỚC 3: LỊCH ĐỔI IP THEO KHUNG GIỜ")
            print("-" * 60)
            print("⏰ Buổi Sáng:")
            print("   → Đổi IP: Nhật hoặc USA")
            print("\n🌙 Buổi Tối:")
            print("   → Đổi IP: Nhật, Nepal hoặc USA")
            
            print("\n" + "="*60)
            print("📋 CHI TIẾT CÁC BƯỚC XỬ LÝ")
            print("="*60)
            
            print("\n🔷 PROFILE BÌNH THƯỜNG:")
            print("-" * 60)
            print("📌 Thao tác:")
            print("   • Nhấp 1 lần: Fake Profile → Me")
            print("   • Với người nổi tiếng: Gõ 'markzuckerberg'")
            print("   • Với doanh nghiệp: Gõ 'meta for business'")
            print("\n📌 Thứ tự xử lý:")
            print("   1-4 → 2-4-1 → 3-1 → 3-2 → 4-1 → 4-2 → 7-1 → 9")
            print("\n📌 Xử lý post:")
            print("   • Nếu có post → Report all dòng 'Fraud or Scam'")
            print("   • Sau đó nhấp tiếp theo thứ tự trên")
            
            print("\n🔶 CHUYÊN NGHIỆP:")
            print("-" * 60)
            print("📌 Fake profile:")
            print("   • Nếu không có avatar → Chỉ fake tên vào biệt danh")
            print("\n📌 Cách nhấp (đơn giản hơn):")
            print("   • 1 lần: Fake Profile → Me")
            print("   • Sau đó: 1-4 → 2-4-1 → 7-1")
            print("\n📌 Trọng tâm:")
            print("   • Chủ yếu cắn post → Nó sẽ die nhanh hơn")
            
            print("\n🔹 CLONE:")
            print("-" * 60)
            print("📌 Thao tác:")
            print("   • Tương tự như Profile Bình Thường")
            print("   • Lưu ý: Nên kẹp clone để dễ die hơn")
            print("   • Áp dụng cùng thứ tự nhấp: 1-4 → 2-4-1 → 3-1 → 3-2 → 4-1 → 4-2 → 7-1 → 9")
            
            print("\n" + "="*60)
            input("\n👉 Nhấn Enter để quay lại menu...")
        
        elif choice == "0":
            print("\n👋 Cảm ơn bạn đã sử dụng tool!")
            break
        
        else:
            print("❌ Lựa chọn không hợp lệ!")


if __name__ == "__main__":
    main()