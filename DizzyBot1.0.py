from mirai import *
import asyncio
import os, random, datetime, time
import re
import requests
import json
import schedule
#import Clock

#Clock = Clock.Clock()

qq = 2968588500 # 字段 qq 的值
HostQQ = 3304339314 # 主人 qq 的值
authKey = '1234567890' # 字段 authKey 的值
MemberList={}       #群成员

app = Mirai(host="localhost", port="8080", authKey=authKey, qq=qq, websocket=True)

status = {} # 机器人状态

waf = ['机器人爬', '机器人傻逼', '傻逼机器人', '群主傻逼', '脑瘫机器人', 'nt机器人'] # 撤回列表
clock_setting_list = [] # 闹钟设置情况

menu = """
Done:
setting.online      开机
setting.offline     关机
weather <city>      查看后三天天气
search <question>   求百度
Todo
setting.clock <time>设置闹钟（暂时已鸽）
clock               查看闹钟（暂时已鸽）
schedule            查看课程表（在做了）
<Anti-setu>         色图监视
<blog-monitor>      博客页监控
"""

""" # 闹钟执行时执行的任务
async def job(app, sender, group):
    print(sender, group) """
    
def fetchWeather(location:str) -> json:
    result = requests.get('https://api.seniverse.com/v3/weather/daily.json', params={
        'key': '4r9bergjetiv1tsd',
        'location': location,
        'language': 'zh-Hans',
        'unit': 'c',
        'days' : 3
    }, timeout=1)
    return result.text

# 好友对话
@app.receiver("FriendMessage")
async def event_gm(app: Mirai, friend: Friend, event: FriendMessage):
    print(Friend, 'friend Message\n')
    text = event.messageChain.__root__[1].text
    if friend.id == HostQQ:
        await app.sendFriendMessage(friend, [
            Plain(text="Hello, Host:"), 
            Plain(text=Friend)
        ])
    else:
        if 'setu' in text:
            await app.sendFriendMessage(friend, [
                Plain('Dont speak about this~~')
            ])

#随机本地setu
def random_setu(dir):
    pathDir = os.listdir(dir)
    dist = random.sample(pathDir, 1)[0]
    return dir+dist

#初始化
@app.subroutine
async def DizzyBot(app: Mirai):
    print("DizzyBot started")
    start_time=datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    groupList = await app.groupList()
    for i in groupList:
        status[i.id]="online"
        memberList = await app.memberList(i.id)
        MemberList[i.id]=memberList
    await app.sendFriendMessage(HostQQ, [
            Plain(text="Hello, Master.\nThis is DizzyBot")
        ])


# 群消息
@app.receiver("GroupMessage")
async def event_gm(app: Mirai, member: Member, group: Group, event: GroupMessage, message: MessageChain):
    #text = event.messageChain.__root__[1].text
    sender =member.id
    global status, MemberList
    # print(event.messageChain.__root__[1].text)
    #print(type(member))
    """ if sender == HostQQ:
        if 'setu' in text:
            await app.sendGroupMessage(group, [
                Plain(text="Hello, Host:"), 
                Plain(text=str(member.memberName)),
                Face(faceId=277)
            ]) """
    print(message)
    print(message.toString())
    print(len(message.__root__))
    # 开机
    if status[member.group.id]=="offline":
        if sender == HostQQ and message.toString()=="[At::target=%i] setting.online"%qq:
            status[member.group.id]="online"
            await app.sendGroupMessage(group,[
                Plain(text="Hello, Master:"), 
                Plain(text=str(member.memberName)),
                Plain(text="\nDizzyBot.online"),
                Face(faceId=277)
            ])
                #record("setting.online group:%s member:%s callResult:%s"%(groupid,send,send in management))
    # 开机时
    else:
        # 通用功能
        if "[At::target=%i]"%qq in message.toString() and len(message.__root__) == 3 and \
            "search" in message.__root__[-1].text:
            question= message.toString()[re.search('search', message.toString()).span()[1] + 1:]
            #question=parse.quote(question)
            await app.sendGroupMessage(group,[
                Plain(text="啧啧啧，都多大了，还不会百度嘛，不会的话谷歌也行啊"),
                Face(faceId=277),
                Plain(text="\nhttps://baidu.sagiri-web.com/?%s"%question)
            ])
        elif message.toString()=="[At::target=%i] menu"%qq:
            await app.sendGroupMessage(group,[
                Plain(text="Hello,{0}".format(sender)), 
                Plain(text=menu),
                Face(faceId=277)
            ])
        if "[At::target=%i]"%qq in message.toString() and len(message.__root__) == 3 and \
            "weather" in message.__root__[-1].text:
            city = message.toString()[re.search('weather', message.toString()).span()[1] + 1:]
            print(city, type(city))
            try:
                text = fetchWeather(city)
                for i in json.loads(text)['results'][0]['daily']:
                    point = city
                    date = i["date"]
                    day_wea = i['text_day']
                    night_wea = i['text_night']
                    tem_low = i['low']
                    tem_high = i['high']
                    rainfall = i['rainfall']
                    win = i['wind_direction']
                    win_speed = i['wind_speed']

                    await app.sendGroupMessage(group,[
                        Plain(text="{0}{1}天气\n".format(point, date)),
                        At(target=sender),
                        Plain(text="\n天气情况：白天{0} 夜间{1}\n".format(day_wea, night_wea)),
                        Plain(text="最高温：%s℃\n"%tem_high),
                        Plain(text="最低温：%s℃\n"%tem_low),
                        Plain(text="降雨量：%s℃\n"%rainfall),
                        Plain(text="风向：%s\n"%win),
                        Plain(text="风速：%s\n"%win_speed)
                    ])
            except:
                await app.sendGroupMessage(group,[
                    Plain(text="憨批玩意，城市名打错了吧，反正我找不到你说的这地方"),
                    At(target=sender)
                ])
        """ #设置时钟
        elif "[At::target=%i]"%qq in message.toString() and len(message.__root__) == 3 and \
        "clock.setting" in message.__root__[-1].text:
            clock = message.toString()[re.search('clock.setting', message.toString()).span()[1] + 1:]
            is_error, clock_list = Clock.time2clock(time=clock)
            if is_error:
                await app.sendGroupMessage(group,[
                        Plain(text="TIMEERROR"), 
                        Face(faceId=277)
                    ])
            Clock.clock_set(clock=clock_list, sender=sender, group=group)
            for i in clock_setting_list:
                if i[1] == "day":
                    await app.sendGroupMessage(group,[
                        Plain(text="用户{0}已经设置了每天的{1}的闹钟！".format(member.memberName, i[2])), 
                        Face(faceId=277)
                    ])
                else:
                    await app.sendGroupMessage(group,[
                        Plain(text="用户{0}已经设置了每周{1}的{2}的闹钟！".format(member.memberName, i[1], i[2])), 
                        Face(faceId=277)
                    ])
            #schedule.run_all(60)

        # 删除单个闹钟
        elif "[At::target=%i]"%qq in message.toString() and len(message.__root__) == 3 and \
        "clock.del" in message.__root__[-1].text:
            clock = message.toString()[re.search('clock.del', message.toString()).span()[1] + 1:]
            _, clocktodel = Clock.time2clock(clock)
            successdelist = Clock.del_clock(sender=sender, clock_wanttodel=clocktodel, group=group)
            if successdelist:
                for a1 in successdelist:
                    if a1[0]:
                        await app.sendGroupMessage(group,[
                                Plain(text="用户{0}已经成功删除了每周{1}的{2}的闹钟！".format(member.memberName, a1[1][0], a1[1][1])), 
                                Face(faceId=277)
                            ])
                    else:
                        await app.sendGroupMessage(group,[
                                Plain(text="用户{0}未能成功删除每周{1}的{2}的闹钟！原因：未找到对应闹钟".format(member.memberName, a1[1][0], a1[1][1])), 
                                Face(faceId=277)
                            ])
            else:
                await app.sendGroupMessage(group,[
                        Plain(text="用户{0}未能成功删除闹钟！原因：未找到对应闹钟".format(member.memberName, a1[1][0], a1[1][1])), 
                        Face(faceId=277)
                    ]) """

        # 分级功能
        if sender == HostQQ:
            if message.toString()=="[At::target=%i] setting.offline"%qq:
                status[member.group.id]="offline"
                await app.sendGroupMessage(group,[
                    Plain(text="Bye, Master:"), 
                    Plain(text=str(member.memberName)),
                    Plain(text="\nDizzyBot.offline"),
                    Face(faceId=277)
                ])
            elif message.toString()=="[At::target=%i]"%qq:
                await app.sendGroupMessage(group,[
                    Plain(text="Hello, Master "), 
                    Plain(text=str(member.memberName)),
                    At(target=HostQQ), 
                    Plain(text=", I am here"),
                    Face(faceId=277)
                ])

            """ # 清除所有闹钟
            elif "[At::target=%i]"%qq in message.toString() and len(message.__root__) == 3 and \
            "clock.clear" in message.__root__[-1].text:
                Clock.clock_clear(sender=sender, group=group)
                print(schedule.jobs)
                await app.sendGroupMessage(group,[
                    Plain(text="清除成功"), 
                    Face(faceId=277)
                ])

            # 查询闹钟
            elif "[At::target=%i]"%qq in message.toString() and len(message.__root__) == 3 and \
            "clock.log" in message.__root__[-1].text:
                await app.sendGroupMessage(group,[
                        Plain(text="Hello master, 现在已设置闹钟如下"), 
                        Face(faceId=277)
                    ])
                all_clock = Clock.clock_log(sender=sender, group=group)
                if all_clock:
                    for i1 in all_clock:
                        #print(i)
                        if i1[1] == "day":
                            await app.sendGroupMessage(group,[
                                    Plain(text="用户{0}设置了每天{1}的闹钟".format(i1[0], i1[2]))
                                ])
                        else:
                            await app.sendGroupMessage(group,[
                                    Plain(text="用户{0}设置了每周{1}{2}的闹钟".format(i1[0], i1[1], i1[2]))
                                ])
                else:
                    await app.sendGroupMessage(group,[
                        Plain(text="查询失败，暂无人设置")
                    ]) """

        # from other qq
        else:
            for i in waf:
                if i in message.toString():
                    await app.sendGroupMessage(group,[
                        Plain(text="就这？"),
                        Face(faceId=178),
                        ])
                    # 撤回
                    await app.revokeMessage(
                        message.__root__[0]
                    )
            if "[At::target=%i]"%HostQQ in message.toString():
                await app.sendGroupMessage(group, 
                [
                    Plain(text='爪巴！爷的主人在忙，有事找爷'), 
                    At(target=member.id), 
                    Face(faceId=178)
                ])
            
            elif "[Image::{" in message.toString():
                Image = message.getFirstComponent(Image)
            
            """ elif "[At::target=%i]"%qq in message.toString() and len(message.__root__) == 3 and \
            "clock.log" in message.__root__[-1].text:
                await app.sendGroupMessage(group,[
                        Plain(text="Hello {0}, 现在已设置闹钟如下".format(sender)), 
                        Face(faceId=277)
                    ])
                all_clock1 = Clock.clock_log(sender=sender, group=group)
                print(all_clock1)
                if all_clock1:
                    for i2 in all_clock1:
                        if sender == i2[3]:
                            if i2[1] == "day":
                                await app.sendGroupMessage(group,[
                                        Plain(text="你设置了每天{0}的闹钟".format(i2[2]))
                                    ])
                            else:
                                await app.sendGroupMessage(group,[
                                        Plain(text="你设置了每周{0}{1}的闹钟".format(i2[1], i2[2]))
                                    ])
                else:
                    await app.sendGroupMessage(group,[
                        Plain(text="查询失败，你还没设置哟"), 
                        Face(faceId=277)
                    ])

            elif "[At::target=%i]"%qq in message.toString() and len(message.__root__) == 3 and \
            "clock.clear" in message.__root__[-1].text:
                await app.sendGroupMessage(group,[
                    Plain(text="你是管理员嘛臭弟弟？爪巴去联系我主人！"), 
                    Face(faceId=277)
                ])
            elif "[At::target=%i]"%qq == message.toString():
                await app.sendGroupMessage(group, 
                [
                    Plain(text='爪巴！别没事at爷'), 
                    At(target=member.id), 
                    Face(faceId=277)
                ]) """

""" async def check_clock():
    while 1:
        print('1')
        schedule.run_pending()
        time.sleep(1) """

# 进群通知
@app.receiver("MemberJoinEvent")
async def member_join(app: Mirai, event: MemberJoinEvent):
    member = event.member.id
    await app.sendGroupMessage(
        event.member.group.id,
        [
            At(target=event.member.id),
            Plain(text="新的lsp已经出现!")
        ]
    )

# 登录
@app.receiver("BotOnlineEvent")
async def bot_login(app: Mirai, event: BotOnlineEvent):
    await app.sendFriendMessage(HostQQ, [
            Plain(text="Hello, Host:"), 
            Plain(text=Friend)
        ])

""" # 防撤回
@app.receiver("GroupRecallEvent")
async def bot_login(app: Mirai, event: GroupRecallEvent):
    print(event.messageId)
    message = app.MessageFromId(event.messageId)
    #print(event.messageId)
    sender = event.authorId
    if sender != qq and sender != HostQQ:
        await app.sendFriendMessage(HostQQ, [
                Plain(text=sender), 
                Plain(text="said:"),
                Plain(text=message)
            ]) """

# 防撤回
""" @app.receiver("GroupRecallEvent")
async def member_join(app: Mirai, event: GroupRecallEvent):
    if event.operator==event.authorId:
        text="%s撤回了他的一条消息呢~↓\n"%qq2name(MemberList[event.group.id],event.operator)
        revokeMsg=Mirai.messageFromId(event.messageId)
        print(revokeMsg)
        revokeMsg.insert(0,Plain(text=text))
        await app.sendGroupMessage(event.group.id,revokeMsg) """

# 临时消息
""" @app.receiver("TempMessage")
async def temp_talk(app: Mirai, event: TempMessage, sender: Member):
    print(sender)
    await app.sendTempMessage(
        event.member.group.id,
        [
            #At(target=event.member.id),
            Plain(text="欢迎进群!")
        ]
    ) """

# 成员解除禁言
@app.receiver("MemberUnmuteEvent")
async def member_join(app: Mirai, event: MemberUnmuteEvent):
    await app.sendGroupMessage(
        event.member.group.id,[
            Plain(text="啊嘞嘞？%s被放出来了呢~"%qq2name(MemberList[event.member.group.id],event.member.id))
        ]
    )


# 加入新群（初始化信息等）
@app.receiver("BotJoinGroupEvent")
async def member_join(app: Mirai, event: BotJoinGroupEvent):
    print("add group")
    await app.sendGroupMessage(
        event.group.id,[
            Plain(text="欸嘿嘿~我来啦！宇宙无敌小可爱纱雾酱华丽登场！")
        ]
    )


#qq号转为昵称
def qq2name(memberList,qq):

    for i in memberList:
        if i.id==qq:
            return i.memberName
    return "qq2Name::Error"

# 权限更改通报
""" @app.receiver("MemberPermissionChangeEvent")
async def permission_change(app: Mirai, event: MemberPermissionChangeEvent\
    , member: Member, group: Group):
    origin = event.origin
    current = event.current
    await app.sendGroupMessage(
        group,
        [
            Plain("恭喜"), 
            At(target=member),
            Plain("从"),
            Plain(origin), 
            Plain("变成"), 
            Plain(current)
        ]
    ) """

def check_clock():
    while 1:
        print("runing")
        schedule.run_pending()
        time.sleep(1)


if __name__ == "__main__":
    app.run()
    
    
    
    