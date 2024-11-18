import requests
import json
import time

def login_system():
    pattern = """
========================================================================================================================
Ｘ　Ｘ　Ｘ　Ｘ　ＴＴＴ　　抢　　抢　　　　答　　答　　　　助助助　助　　手手手手手手手
Ｘ　Ｘ　Ｘ　Ｘ　　Ｔ　　抢抢抢抢　抢　　　答答　答答答　　助　助助助助　　　　手　　　　　１　　　　　　　０
　Ｘ　　　Ｘ　　　Ｔ　　　抢　　　　抢　答　答答　答　　　助助助　助助　　手手手手手　　１１　　　　　　０　０
　Ｘ　　　Ｘ　　　Ｔ　　　抢抢抢抢抢　　　　答答答　　　　助　助　助助　　　　手　　　　　１　　　　　　０　０
Ｘ　Ｘ　Ｘ　Ｘ　　Ｔ　　抢抢　抢　抢　　答答　　　答答　　助助助　助助　手手手手手手手　　１　　　　　　０　０
Ｘ　Ｘ　Ｘ　Ｘ　　Ｔ　　　抢　抢　　抢　　　答答答　　　　助　助助　助　　　　手　　　　１１１　　．　　　０
　　　　　　　　　　　　抢抢　抢抢抢抢　　　答答答　　　助助助　助　助　　　手手
========================================================================================================================
                               GitHub地址:https://github.com/NMDDSB/XXT-Assistant
"""
    print(pattern)
    while True:

        username = input("========================================================================================================================\nXXT账号: ")
        password = input("XXT密码: ")

        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'
        }


        try:
            response = requests.post('https://passport2.chaoxing.com/api/login', data={
                'name': username,
                'pwd': password,
                'schoolid': "",
                'verify': 0
            }, headers=headers)

            # 获取网页返回内容
            content = response.json()

            if content.get('result'):
                uname = content.get('uname')
                realname = content.get('realname')
                print(f"========================================================================================================================\nXXT抢答助手：登录成功！学号:{uname} 姓名:{realname}！\n========================================================================================================================")


                cookies = response.cookies.get_dict()



                course_response = requests.get('https://mooc1-api.chaoxing.com/mycourse/backclazzdata?view=&rss=1', cookies=cookies, headers=headers)
                course_content = course_response.text


                try:
                    data = json.loads(course_content)


                    extracted_data = []



                    for channel in data.get('channelList', []):
                        content = channel.get('content', {})  # 使用.get()避免KeyError
                        # 提取channel_key
                        channel_key = channel.get('key', '')
                        # 遍历content中的course数据
                        for course in content.get('course', {}).get('data', []):  # 使用.get()避免KeyError
                            # 提取所需的字段
                            extracted_item = {
                                'belongSchoolId': course.get('belongSchoolId'),
                                'id': course.get('id'),
                                'name': course.get('name'),
                                'teacherfactor': course.get('teacherfactor'),  # 添加teacherfactor字段
                                'channel_key': channel_key  # 添加channel_key字段
                            }
                            # 将提取的数据添加到列表中
                            extracted_data.append(extracted_item)



                    while True:
                        # 打印提取的数据，一行一个字段，并添加序列号
                        for i, item in enumerate(extracted_data, start=1):
                            
                            print(f"Serial Number: {i} | Belong School ID: {item.get('belongSchoolId')} | ID: {item.get('id')} | Key: {item.get('channel_key')} | Name: {item.get('name')} | Teacher Factor: {item.get('teacherfactor')}\n========================================================================================================================")

                        # 用户选择课程
                        choice_input = input("XXT抢答助手提示您请输入需抢答课程的序号（输入'tc'退出登录）: ")
                        print("========================================================================================================================")
                        if choice_input.lower() == 'tc':
                            print("========================================================================================================================\n退出登录成功！\n========================================================================================================================")
                            break

                        try:
                            choice = int(choice_input)
                            if 1 <= choice <= len(extracted_data):
                                selected_course = extracted_data[choice - 1]
                                belong_school_id = selected_course['belongSchoolId']
                                course_id = selected_course['id']
                                channel_key = selected_course['channel_key']

                                # 构建课程URL
                                activity_url = f"https://mobilelearn.chaoxing.com/v2/apis/active/student/activelist?fid={belong_school_id}&courseId={course_id}&classId={channel_key}&showNotStartedActive=0&_=1731829127285"

                                # 循环执行
                                for attempt in range(30):
                                    # 使用cookie发送GET请求获取课程活动数据
                                    activity_response = requests.get(activity_url, cookies=cookies, headers=headers)
                                    activity_content = activity_response.json()

                                    # 解析课程数据
                                    active_list = activity_content.get('data', {}).get('activeList', [])
                                    active_id = None
                                    for active in active_list:
                                        if active.get('status') == 1:
                                            active_id = active.get('id')
                                            break

                                    if active_id:
                                        # 构建请求URL
                                        second_url = "https://mobilelearn.chaoxing.com/v2/apis/answer/stuAnswer"
                                        second_params = {
                                            "classId": channel_key,
                                            "courseId": course_id,
                                            "activeId": active_id,
                                            "enterAnswer": ""
                                        }

                                        # 使用cookie发送POST请求
                                        second_response = requests.post(second_url, params=second_params, cookies=cookies, headers=headers)
                                        second_content = second_response.json()

                                        print(f"抢答第 {attempt + 1} 次尝试：正在激情抢答中！:")
                                        formatted_output = json.dumps(second_content, ensure_ascii=False, indent=4)

                                        # 处理特定的JSON返回内容
                                        if second_content == {"result":0,"msg":None,"data":None,"errorMsg":"倒计时中...未开始抢答"}:
                                            print("倒计时中...未开始抢答")
                                        elif second_content.get('msg') == "抢答成功":
                                            print("抢答成功！嘀嘀嘀道道道！")
                                            break
                                        elif second_content.get('msg') == "学生已抢答":
                                            print("学生已抢答！嘀嘀嘀道道道！")
                                            break
                                    else:
                                        print(f"抢答第 {attempt + 1} 次尝试：正在激情抢答中！")

                                    # 等待1秒
                                    time.sleep(0.5)
                                else:
                                    print("抢答助手提示您没有找到抢答哟！")


                                # 显示提示信息并等待用户输入
                                post_attempt_action = input("========================================================================================================================\nXXT抢答助手提示您抢答执行完毕！（输入'tc'退出登录或输入'kc'返回课程序号）: ").lower()
                                if post_attempt_action == 'tc':
                                    print("========================================================================================================================\nXXT抢答助手提示您退出登录成功！\n========================================================================================================================")
                                    break
                                elif post_attempt_action != 'kc':
                                    print("无效的选择，请重新操作。")

                            else:
                                print("无效的序号，请重新选择。")
                        except ValueError:
                            print("请输入有效的数字或 'kc' 返回登录页面。")

                except json.JSONDecodeError as e:
                    print(f"JSON解码错误: {e}")
                except KeyError as e:
                    print(f"键不存在错误: {e}")

            else:
                error_msg = content.get('errorMsg', "未知错误")
                print(f"========================================================================================================================\nXXT抢答助手登录失败！提示:{error_msg}")

        except requests.exceptions.RequestException as e:
            print(f"请求发生错误: {e}")

if __name__ == "__main__":
    login_system()