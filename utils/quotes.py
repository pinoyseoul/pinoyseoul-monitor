# -*- coding: utf-8 -*-
"""
Provides motivational quotes for daily summaries.

This module contains lists of pre-defined, Korean-themed quotes for various
times of the day and a function to retrieve a random one.
"""

import random

# -----------------------------------------------------------------------------
# Morning Greetings
# -----------------------------------------------------------------------------
morning_greetings = [
    "Good morning, team! Here is today's status summary:",
    "Hello everyone, here's your daily update:",
    "Rise and shine! Time for the morning status report:",
    "A new day, a new report! Good morning:",
    "Morning, PinoySeoul Media! Here's the latest:",
    "Top of the morning! Your daily infrastructure brief:",
    "Hope you're having a great start! Here's the system status:",
    "Good day! Bringing you the latest on our services:",
    "Greetings! Your automated morning check-in is here:",
    "Hello, early birds! Here's what's happening across our platforms:"
]

# -----------------------------------------------------------------------------
# Morning Closings
# -----------------------------------------------------------------------------
morning_closings = [
    "Have a productive day! 🚀",
    "Wishing you a successful day ahead!",
    "Go forth and conquer! 💪",
    "Stay awesome, team! ✨",
    "Make today amazing! 🌟",
    "Here's to a smooth and efficient day!",
    "Keep up the great work!",
    "May your day be filled with success!",
    "Cheers to a productive day!",
    "Let's make it a great one!"
]

# -----------------------------------------------------------------------------
# Evening Greetings
# -----------------------------------------------------------------------------
evening_greetings = [
    "Good evening! Today, the radio station reached a total of",
    "Hello everyone, here's the latest from the airwaves. We reached",
    "As the day winds down, here's the listener count:",
    "Night, PinoySeoul Media! Listener summary incoming. We saw",
    "Wrapping up the day with our listener summary. Today's total is",
]

# -----------------------------------------------------------------------------
# Evening Closings
# -----------------------------------------------------------------------------
evening_closings = [
    "Amazing work, everyone. Let's keep it up! 🎉",
    "Great job today! Rest up for tomorrow. 🌙",
    "Keep those listeners tuned in! 📻",
    "Another successful day on air! 🎧",
    "Thanks for a great day of broadcasting! 🎤",
    "Wishing you a peaceful evening!",
    "Sweet dreams and happy listening!",
    "Looking forward to another great day on the air!",
    "Keep the good vibes going!",
    "That's a wrap for today's listeners. See you tomorrow!"
]


# -----------------------------------------------------------------------------
# Korean-Themed Morning Quotes (Productivity & A New Day)
# -----------------------------------------------------------------------------
morning_quotes = [
    "시작이 반이다. - Starting is half the battle. A good start to your day is half the work done.",
    "호랑이에게 물려가도 정신만 차리면 산다. - Even if a tiger is about to eat you, you can survive if you keep your wits. Stay focused and conquer the day!",
    "오늘 걷지 않으면 내일은 뛰어야 한다. - If you don't walk today, you'll have to run tomorrow. Seize the day!",
    "천 리 길도 한 걸음부터. - A journey of a thousand miles begins with a single step. Make the first move today.",
    "일찍 일어나는 새가 벌레를 잡는다. - The early bird catches the worm. May your morning be productive.",
    "뜻이 있는 곳에 길이 있다. - Where there's a will, there's a way. Set your intentions for a great day.",
    "고생 끝에 낙이 온다. - At the end of hardship comes happiness. Push through your tasks today.",
    "산을 옮기는 사람은 작은 돌부터 옮긴다. - The person who moves a mountain starts by carrying away small stones. Focus on one task at a time.",
    "시간은 금이다. - Time is gold. Make every moment of your day count.",
    "낮말은 새가 듣고 밤말은 쥐가 듣는다. - Birds hear the words spoken during the day, and mice hear those at night. Let your actions today be worth talking about.",
    "하늘은 스스로 돕는 자를 돕는다. - Heaven helps those who help themselves. Take initiative this morning.",
    "백지장도 맞들면 낫다. - Two heads are better than one. Collaborate and succeed today.",
    "오늘 할 일을 내일로 미루지 말라. - Don't put off until tomorrow what you can do today.",
    "땀은 배신하지 않는다. - Sweat does not betray you. Your hard work today will pay off.",
    "시작이 좋아야 끝도 좋다. - A good start leads to a good end. Make your morning count.",
    "최고의 복수는 엄청난 성공이다. - The best revenge is massive success. Let that motivate your day.",
    "성공은 가장 끈기 있는 사람에게 찾아온다. - Success comes to the most persevering. Stay persistent.",
    "서두르면 일을 그르친다. - Haste makes waste. Be productive, but be mindful.",
    "행동은 모든 성공의 열쇠이다. - Action is the foundational key to all success. Get started!",
    "작은 성취가 모여 큰 성공을 이룬다. - Small achievements, when gathered, make a great success. Aim for small wins today.",
    "아침은 하루의 황금 시간이다. - Morning is the golden time of the day. Use it wisely.",
    "부지런한 자에게는 가난이 없다. - There is no poverty for the diligent. Your efforts will be rewarded.",
    "계획 없는 목표는 한낱 꿈에 불과하다. - A goal without a plan is just a wish. Plan your day for success.",
    "성공의 아침은 부지런함으로 시작된다. - The morning of success begins with diligence.",
    "오늘의 땀은 내일의 열매를 맺는다. - Today's sweat bears tomorrow's fruit.",
    "가장 높은 산도 첫 걸음부터 시작된다. - Even the highest mountain begins with a single step. Take yours now.",
    "기회는 준비된 자에게 온다. - Opportunity comes to the prepared mind. Prepare for a great day.",
    "실패는 성공의 어머니다. - Failure is the mother of success. Don't be afraid to try new things today.",
    "아침 해처럼 당신의 가능성도 매일 새롭게 떠오른다. - Like the morning sun, your potential rises anew each day.",
    "노력하는 자에게 불가능은 없다. - Nothing is impossible for a person who tries. Challenge yourself today.",
    "한 번의 실패에 좌절하지 마라. - Don't be discouraged by a single failure. Every day is a new chance.",
    "성실함이 최고의 재능이다. - Sincerity is the best talent. Be sincere in your work today.",
    "오늘의 작은 습관이 내일의 큰 차이를 만든다. - Today's small habits make tomorrow's big difference.",
    "가장 어두운 시간은 해 뜨기 바로 직전이다. - The darkest hour is just before the dawn. A bright day awaits.",
    "성공은 매일의 노력이 쌓인 결과이다. - Success is the result of daily accumulated effort.",
    "자신을 믿는 것이 성공의 첫걸음이다. - Believing in yourself is the first step to success.",
    "오늘의 집중이 내일의 현실을 만든다. - Today's focus creates tomorrow's reality.",
    "가장 큰 위험은 위험 없는 삶이다. - The biggest risk is a life without risk. Step out of your comfort zone.",
    "배움에는 끝이 없다. - There is no end to learning. Learn something new this morning.",
    "인내는 쓰지만 그 열매는 달다. - Patience is bitter, but its fruit is sweet. Be patient with your progress.",
    "강한 자는 자기 자신을 이기는 자다. - The strong person is the one who overcomes themselves. Win your morning.",
    "꿈을 크게 가져라, 깨져도 그 조각이 크다. - Dream big, even if it breaks, the pieces are big. Aim high today.",
    "오늘의 한 시간이 내일의 하루를 좌우한다. - One hour today determines a whole day tomorrow.",
    "긍정적인 생각이 긍정적인 결과를 낳는다. - Positive thoughts lead to positive results. Start with a good mindset.",
    "가장 좋은 길은 항상 가장 어려운 길이다. - The best path is always the most difficult one. Embrace the challenge.",
    "성공은 열정의 산물이다. - Success is the product of passion. Find your passion this morning.",
    "작은 물방울이 모여 강을 이룬다. - Small drops of water gather to form a river. Every little effort counts.",
    "오늘의 당신은 어제의 당신보다 낫다. - The you of today is better than the you of yesterday. Keep growing.",
    "위대한 일은 작은 일들이 모여 이루어진다. - Great things are done by a series of small things brought together.",
    "아침의 계획이 하루의 성공을 보장한다. - A morning plan guarantees a day of success.",
    "가장 큰 영광은 결코 넘어지지 않는 데 있는 것이 아니라, 넘어질 때마다 일어서는 데 있다. - Our greatest glory is not in never falling, but in rising every time we fall.",
    "성공하려면 귀는 열고 입은 닫아라. - To succeed, open your ears and close your mouth. Listen and learn today.",
    "오늘의 노력이 당신의 미래를 결정한다. - Your efforts today will define your future.",
    "가장 현명한 사람은 배우는 사람이다. - The wisest person is one who is always learning.",
    "성공은 행동과 연결되어 있다. - Success is connected with action. Keep moving forward.",
    "오늘의 실천이 내일의 당신을 만든다. - Today's practice builds the you of tomorrow.",
    "가장 큰 장애물은 자신의 의심이다. - The biggest obstacle is your own doubt. Believe in yourself.",
    "성공은 용기 있는 자의 것이다. - Success belongs to the brave. Be courageous today.",
    "오늘의 최선이 내일의 표준이 되게 하라. - Let today's best be tomorrow's standard.",
    "가장 큰 힘은 긍정적인 태도에 있다. - The greatest power lies in a positive attitude.",
    "성공은 기회를 잡는 것이다. - Success is about seizing opportunities. Be ready for them today.",
    "오늘의 인내가 내일의 힘이 된다. - Today's patience becomes tomorrow's strength.",
    "가장 큰 지혜는 시간을 잘 쓰는 것이다. - The greatest wisdom is to use time well.",
    "성공은 작은 성공의 연속이다. - Success is a series of small successes.",
    "오늘의 도전이 내일의 성장을 이끈다. - Today's challenge leads to tomorrow's growth.",
    "가장 큰 투자는 자기 자신에게 하는 투자다. - The best investment is in yourself. Invest in your skills today.",
    "성공은 마음가짐의 문제다. - Success is a matter of mindset. Cultivate a winning one.",
    "오늘의 열정이 내일의 기적을 만든다. - Today's passion creates tomorrow's miracle.",
    "가장 큰 적은 나태함이다. - The greatest enemy is laziness. Overcome it this morning.",
    "성공은 꾸준함의 결과다. - Success is the result of consistency. Keep at it.",
    "오늘의 한 걸음이 미래의 큰 도약을 만든다. - One step today makes a great leap for the future.",
    "가장 큰 변화는 작은 시작에서 비롯된다. - The biggest changes come from small beginnings.",
    "성공은 준비와 기회가 만나는 것이다. - Success is where preparation and opportunity meet.",
    "오늘의 노력이 헛되지 않을 것이다. - Today's effort will not be in vain.",
    "가장 큰 무기는 긍정이다. - The greatest weapon is positivity.",
    "성공은 자신감에서 시작된다. - Success starts with confidence. Be confident in your abilities.",
    "오늘의 땀방울이 내일의 미소를 만든다. - Today's teardrop of sweat creates tomorrow's smile.",
    "가장 큰 성공은 자기 자신을 이기는 것이다. - The greatest success is conquering yourself.",
    "성공은 결코 우연이 아니다. - Success is never an accident. It's hard work.",
    "오늘의 계획이 내일의 지도가 된다. - Today's plan becomes tomorrow's map.",
    "가장 큰 힘은 희망이다. - The greatest strength is hope. Be hopeful for the day ahead.",
    "성공은 포기하지 않는 것이다. - Success is not giving up. Persevere.",
    "오늘의 집중이 내일의 성과를 결정한다. - Today's focus determines tomorrow's results.",
    "가장 큰 지혜는 겸손이다. - The greatest wisdom is humility. Be open to learning.",
    "성공은 작은 디테일에 있다. - Success is in the small details. Pay attention to them.",
    "오늘의 노력이 당신을 더 강하게 만든다. - Today's effort makes you stronger.",
    "가장 큰 성공은 다른 사람을 돕는 것이다. - The greatest success is helping others. Make a positive impact.",
    "성공은 과정이지 결과가 아니다. - Success is a journey, not a destination. Enjoy the process.",
    "오늘의 긍정이 내일의 행복을 만든다. - Today's positivity creates tomorrow's happiness.",
    "가장 큰 힘은 인내심에 있다. - The greatest power lies in patience.",
    "성공은 행동하는 자의 것이다. - Success belongs to those who act. Take action now.",
    "오늘의 배움이 내일의 지혜가 된다. - Today's learning becomes tomorrow's wisdom.",
    "가장 큰 성공은 만족하는 것이다. - The greatest success is contentment. Be grateful for today.",
    "성공은 습관의 결과다. - Success is the result of habits. Build good ones.",
    "오늘의 노력이 당신의 가치를 증명한다. - Today's effort proves your worth.",
    "가장 큰 힘은 용서에 있다. - The greatest strength is in forgiveness. Start the day with a clear mind.",
    "성공은 마음의 평화다. - Success is peace of mind. Find your focus.",
    "오늘의 시작이 당신의 미래를 바꾼다. - Today's start changes your future."
]

# -----------------------------------------------------------------------------
# Korean-Themed Evening Quotes (Success & Reflection)
# -----------------------------------------------------------------------------
evening_quotes = [
    "수고했어, 오늘도. - You worked hard today. Well done.",
    "오늘의 성공은 어제의 노력 덕분이다. - Today's success is thanks to yesterday's effort. Reflect on your hard work.",
    "성공은 준비된 자에게 찾아온다. - Success comes to those who are prepared. Your efforts today are preparations for tomorrow.",
    "하루를 마무리하며, 내일의 성공을 꿈꿔라. - As you end the day, dream of tomorrow's success.",
    "가장 큰 영광은 넘어지지 않는 것이 아니라, 넘어질 때마다 일어나는 것이다. - The greatest glory is not in never falling, but in rising every time we fall. Today's challenges build tomorrow's strength.",
    "성공은 여정이지, 목적지가 아니다. - Success is a journey, not a destination. Appreciate the progress you made today.",
    "오늘의 노력이 내일의 당신을 만든다. - Today's efforts build the you of tomorrow.",
    "쉬는 것도 일의 연장이다. - Resting is an extension of work. A productive evening includes rest.",
    "성공적인 하루의 끝은 평화로운 밤이다. - The end of a successful day is a peaceful night.",
    "작은 별들이 모여 은하수를 이룬다. - Small stars gather to form the Milky Way. Every small success today contributes to a bigger picture.",
    "결과보다는 과정이 중요하다. - The process is more important than the result. Reflect on how you've grown today.",
    "잘 자는 것이 내일의 성공을 위한 첫걸음이다. - Sleeping well is the first step to tomorrow's success.",
    "오늘의 한 페이지를 잘 마무리했다. - You have finished a page of your life well today.",
    "노력은 결코 배반하지 않는다. - Effort never betrays you. Trust in the work you did today.",
    "성공의 비결은 꾸준함이다. - The secret to success is consistency. Well done for being consistent today.",
    "매일 밤, 당신은 별처럼 빛났다. - Every night, you shined like a star.",
    "오늘의 수고가 미래의 밑거름이 된다. - Today's hard work becomes the foundation for the future.",
    "꿈을 향해 한 걸음 더 나아간 하루. - A day you took one more step towards your dream.",
    "최고의 내일은 오늘을 충실히 보낸 밤에 온다. - The best tomorrow comes after a night where you've lived today to the fullest.",
    "성공은 작은 습관에서 시작된다. - Success begins with small habits. Good job maintaining them today.",
    "오늘의 쉼이 내일의 에너지가 된다. - Today's rest becomes tomorrow's energy.",
    "하루의 끝은 새로운 시작을 의미한다. - The end of the day means a new beginning. Rest well for it.",
    "성공적인 사람은 밤에 내일의 계획을 세운다. - A successful person plans for tomorrow in the evening.",
    "오늘의 경험이 당신을 더 지혜롭게 만들었다. - Today's experiences have made you wiser.",
    "밤은 깊었지만, 당신의 꿈은 더 밝게 빛난다. - The night is deep, but your dreams shine brighter.",
    "오늘의 성과에 만족하고, 내일의 가능성에 기대하라. - Be content with today's achievements and look forward to tomorrow's potential.",
    "성공은 하루아침에 이루어지지 않는다. 오늘의 노력을 기억하라. - Success isn't built in a day. Remember the effort you put in today.",
    "평온한 밤이 창의적인 내일을 만든다. - A calm night creates a creative tomorrow.",
    "오늘의 당신은 충분히 훌륭했다. - You were more than enough today.",
    "성공의 길은 계속 나아가는 것이다. 오늘도 한 걸음 나아갔다. - The path to success is to keep going. You've taken another step today.",
    "밤하늘의 별처럼, 당신의 노력도 빛나고 있다. - Like the stars in the night sky, your efforts are shining.",
    "오늘의 마무리가 내일의 시작을 결정한다. - How you finish today determines how you'll start tomorrow.",
    "성공은 감사하는 마음에서 온다. 오늘 하루에 감사하라. - Success comes from a grateful heart. Be thankful for the day.",
    "오늘의 배움에 감사하며 편안한 밤을 보내라. - Be grateful for today's lessons and have a peaceful night.",
    "당신의 노력은 결코 헛되지 않았다. - Your hard work was never in vain.",
    "성공은 인내심 있는 자에게 온다. 오늘도 잘 견뎠다. - Success comes to those who have patience. You endured well today.",
    "오늘의 작은 승리를 축하하라. - Celebrate your small victories of the day.",
    "밤은 휴식의 시간이며, 재충전의 시간이다. - The night is a time for rest and recharging.",
    "오늘의 당신을 자랑스러워하라. - Be proud of yourself for what you did today.",
    "성공은 목적지가 아니라, 그 과정에서 얻는 것이다. - Success is not a destination, but what you gain in the process.",
    "오늘의 노력이 모여 당신의 미래가 된다. - The collection of your efforts today becomes your future.",
    "가장 어두운 밤도 결국 아침을 맞이한다. - Even the darkest night will end and the sun will rise.",
    "오늘의 당신은 최선을 다했다. - You did your best today. That's what matters.",
    "성공은 자기 자신과의 싸움에서 이기는 것이다. - Success is winning the battle against yourself. You won today.",
    "오늘의 경험을 발판 삼아 내일 더 높이 날아오르라. - Use today's experience as a stepping stone to fly higher tomorrow.",
    "밤은 성찰의 시간이다. 오늘 하루를 돌아보라. - Night is a time for reflection. Look back on your day.",
    "오늘의 당신은 어제보다 더 강해졌다. - You are stronger today than you were yesterday.",
    "성공은 꾸준한 사람의 것이다. 오늘도 수고했다. - Success belongs to the persistent. Good work today.",
    "오늘의 끝에서 내일의 희망을 보라. - See the hope of tomorrow at the end of today.",
    "당신의 꿈이 밤하늘의 별보다 더 빛나길. - May your dreams shine brighter than the stars in the night sky.",
    "오늘의 노고에 박수를 보낸다. - I applaud your hard work today.",
    "성공은 준비된 마음에서 시작된다. 편안한 밤으로 마음을 준비하라. - Success starts with a prepared mind. Prepare it with a peaceful night.",
    "오늘의 당신은 충분히 빛났다. - You shined brightly enough today.",
    "성공은 하루의 합계다. 오늘 하루를 잘 더했다. - Success is the sum of your days. You've added today well.",
    "오늘의 땀이 내일의 길을 밝힐 것이다. - Today's sweat will light up tomorrow's path.",
    "밤은 꿈을 꾸는 시간이 아니라, 꿈을 준비하는 시간이다. - Night is not for dreaming, but for preparing for your dreams.",
    "오늘의 당신을 믿어라. 내일의 당신은 더 강할 것이다. - Believe in yourself today. The you of tomorrow will be even stronger.",
    "성공은 작은 성공들의 합이다. 오늘 하루도 성공적이었다. - Success is the sum of small successes. Today was another success.",
    "오늘의 마무리를 축하한다. - Congratulations on finishing the day strong.",
    "밤의 고요함 속에서 내일의 에너지를 찾아라. - Find tomorrow's energy in the tranquility of the night.",
    "오늘의 당신은 역사의 한 페이지를 썼다. - You wrote a page of history today.",
    "성공은 방향을 잃지 않는 것이다. 오늘도 잘 나아갔다. - Success is not losing direction. You moved forward well today.",
    "오늘의 노력이 당신을 배신하지 않을 것이다. - Your efforts today will not betray you.",
    "밤은 새로운 아이디어를 위한 시간이다. - The night is a time for new ideas. Let your mind wander.",
    "오늘의 당신은 승리자다. - You are a winner today.",
    "성공은 만족할 줄 아는 것이다. 오늘 하루에 만족하라. - Success is knowing how to be content. Be content with today.",
    "오늘의 당신이 내일의 당신을 만든다. - The you of today creates the you of tomorrow.",
    "밤은 치유의 시간이다. 오늘 하루의 피로를 풀어라. - Night is a time for healing. Relieve the fatigue of the day.",
    "오늘의 당신은 충분히 노력했다. - You have worked hard enough today.",
    "성공은 기쁨을 나누는 것이다. 오늘의 성과를 사랑하는 이들과 나눠라. - Success is about sharing joy. Share today's achievements with loved ones.",
    "오늘의 당신은 아름다웠다. - You were beautiful today.",
    "밤은 감사하는 시간이다. 오늘 하루에 감사하라. - Night is a time for gratitude. Be thankful for the day.",
    "오늘의 당신은 영웅이었다. - You were a hero today.",
    "성공은 자신을 사랑하는 것에서 시작된다. 오늘 하루 수고한 자신을 사랑해주어라. - Success starts with loving yourself. Love yourself for working hard today.",
    "오늘의 당신은 최고였다. - You were the best today.",
    "밤은 별들이 당신을 위해 빛나는 시간이다. - The night is when the stars shine for you.",
    "오늘의 당신은 모든 것을 이겨냈다. - You overcame everything today.",
    "성공은 평화로운 마음에서 온다. 편안한 밤을 보내라. - Success comes from a peaceful mind. Have a restful night.",
    "오늘의 당신은 세상을 더 나은 곳으로 만들었다. - You made the world a better place today.",
    "밤은 내일을 위한 선물이다. - The night is a gift for tomorrow.",
    "오늘의 당신은 기적이었다. - You were a miracle today.",
    "성공은 계속해서 꿈꾸는 것이다. 좋은 꿈을 꾸어라. - Success is to keep dreaming. Have sweet dreams.",
    "오늘의 당신은 희망이었다. - You were hope today.",
    "밤은 당신의 노력을 위로하는 시간이다. - The night is a time to comfort you for your hard work.",
    "오늘의 당신은 빛이었다. - You were a light today.",
    "성공은 나눔에 있다. 오늘의 기쁨을 나눠라. - Success is in sharing. Share the joy of today.",
    "오늘의 당신은 사랑이었다. - You were love today.",
    "밤은 당신을 위한 휴식처다. - The night is a sanctuary for you.",
    "오늘의 당신은 모든 것을 해냈다. - You accomplished everything today.",
    "성공은 감사함에 있다. 오늘 하루에 감사하라. - Success is in gratitude. Be thankful for today.",
    "오늘의 당신은 완벽했다. - You were perfect today.",
    "밤은 당신의 성공을 축하하는 시간이다. - The night is a time to celebrate your success.",
    "오늘의 당신은 미래를 만들었다. - You created the future today."
]

def get_random_phrase(phrase_type: str) -> str:
    """
    Selects a random phrase based on the specified type.

    Args:
        phrase_type (str): The type of phrase to get (e.g., 'morning_greeting',
                           'evening_closing').

    Returns:
        A randomly selected phrase string.
    """
    if phrase_type == 'morning_greeting':
        return random.choice(morning_greetings)
    elif phrase_type == 'morning_closing':
        return random.choice(morning_closings)
    elif phrase_type == 'evening_greeting':
        return random.choice(evening_greetings)
    elif phrase_type == 'evening_closing':
        return random.choice(evening_closings)
    return ""

def get_random_quote(quote_type: str) -> str:
    """
    Selects a random quote based on the specified type.

    Args:
        quote_type (str): The type of quote to get ('morning' or 'evening').

    Returns:
        A randomly selected quote string.
    """
    if quote_type == 'morning':
        return random.choice(morning_quotes)
    elif quote_type == 'evening':
        return random.choice(evening_quotes)
    return "Have a great day!"
