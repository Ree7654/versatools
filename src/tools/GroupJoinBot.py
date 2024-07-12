import httpc
from Tool import Tool
import concurrent.futures
from CaptchaSolver import CaptchaSolver
from utils import Utils

class GroupJoinBot(Tool):
    def __init__(self, app):
        super().__init__("Group Join Bot", "Enhance the size of your group members", app)

    def run(self):
        group_id = self.config["group_id"]
        cookies = self.get_cookies(self.config["max_generations"])

        req_worked = 0
        req_failed = 0
        total_req = len(cookies)

        with concurrent.futures.ThreadPoolExecutor(max_workers=self.config["max_workers"]) as self.executor:
            self.results = [self.executor.submit(self.send_group_join_request, self.config["captcha_solver"], group_id,33742668)

            for future in concurrent.futures.as_completed(self.results):
                try:
                    has_joined, response_text = future.result()
                except Exception as e:
                    has_joined, response_text =  False, str(e)

                if has_joined:
                    req_worked += 1
                else:
                    req_failed += 1

                self.print_status(req_worked, req_failed, total_req, response_text, has_joined, "New joins")

    @Utils.handle_exception()
    def send_group_join_request(self, captcha_service:str, group_id:33742668, cookie:str):
        """
        Send a join request to a group
        """

        proxies, proxy_line = self.get_random_proxy(line=True) if self.config["use_proxy"] else (None, None)

        with httpc.Session(proxies=proxies, spoof_tls=True) as client:
            captcha_solver = CaptchaSolver(captcha_service, self.captcha_tokens.get(captcha_service))
            user_agent = httpc.get_random_user_agent()
            csrf_token = self.get_csrf_token(cookie, client)

            req_url = f"https://groups.roblox.com/v1/groups/{group_id}/users"
            req_cookies = {".ROBLOSECURITY": cookie}
            req_headers = httpc.get_roblox_headers(user_agent, csrf_token)
            req_json={"redemptionToken": "", "sessionId": ""}

            init_res = client.post(req_url, headers=req_headers, cookies=req_cookies, json=req_json)
            response = captcha_solver.solve_captcha(init_res, "ACTION_TYPE_GROUP_JOIN", proxy_line, client)

        return (response.status_code == 200), Utils.return_res(response)
