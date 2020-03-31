import discord
from discord.ext import commands
token = "NjYyNDIxODg4NzEwMjEzNjM2.Xg9yPg.yczDwge3Uj_gBTjQ-WQsX1hxxio"
client = commands.Bot(command_prefix="&")
badchannels = []
bad = False


# web scraping
def choose_problem_type(ptword):
    ptword = ptword.lower()
    ptword = ptword.replace(" ", "")
    pttypes = ["simplemath", "datastructures", "graphtheory", "stringalgorithms",
               "dynamicprogramming", "divideandconquer", "greedyalgorithms",
               "advancedmath", "intermediatemath", "adhoc", "bruteforce",
               "implementation", "regularexpressions", "recursion", "geometry",
               "gametheory", "simulation", "uncategorized"]
    ptnums = []
    for type in range(len(pttypes)):
        if pttypes[type] in ptword:
            ptnums.append(type+1)

    final = "https://dmoj.ca/problems/?show_types=1"
    for num in ptnums:
        final += "&type="+str(num)

    return final


def get_point_range(urll, lower, upper):
    if not lower:
        if not upper:
            return urll
        elif upper > 0:
            urll += "&point_end=" + str(upper)
    elif not upper:
        if lower > 0:
            urll += "&point_start=" + str(lower)
    else:
        if upper >= lower > 0:
            urll += "&point_start=" + str(lower) + "&point_end=" + str(upper)

    return urll


def point_input(inp):
    inp = inp.replace(" ", "")
    if inp == "":
        return None
    try:
        return int(inp)
    except ValueError:
        return 999


# replaced driver with requests library
# maybe be subject to change
def get_problems(baseurl):
    import requests
    import os
    from random import choice
    from bs4 import BeautifulSoup
    from selenium import webdriver
    numberofpages = 49
    problemlist = []

    for pg in range(1, numberofpages+1):
        # modifying url for each page
        url = baseurl
        url += "&page="+str(pg)

        chrome_options = webdriver.ChromeOptions()
        chrome_options.binary_location = os.environ.get("GOOGLE_CHROME_BIN")
        chrome_options.add_argument("--headless")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--no-sandbox")
        driver = webdriver.Chrome(executable_path=os.environ.get("CHROMEDRIVER_PATH"), chrome_options=chrome_options)

        driver.get(url)
        content = driver.page_source
        # page = requests.get(url)
        soup = BeautifulSoup(content, 'html.parser')
        # dmoj url: dmoj.ca/problems/?showtypes=1&type=(specifiedtype)
        # &point_start=(lowerbound)&point_end=(upperbound)&page=(pg#)

        # reaching the end page
        try:
            table = soup.find(id="problem-table").find("tbody").find_all("tr")
        except AttributeError:
            break

        for problem in table:
            problemlist.append(problem.find('a').get('href'))

    final = "https://dmoj.ca"+choice(problemlist)
    return final


def scrape(problemtype, lowerp, higherp):
    from selenium import webdriver

    # driver = webdriver.Chrome(executable_path=r'C:/webdrivers/chromedriver.exe')
    url = get_point_range(choose_problem_type(problemtype), lowerp, higherp)

    final = get_problems(url)
    return final


def do(inputt):
    temp = [x for x in inputt.split("-")]
    if len(temp) < 3:
        return None, True

    ptype = temp[0]
    lowerpointrange = point_input(temp[1])
    higherpointrange = point_input(temp[2])

    if lowerpointrange == 999 or higherpointrange == 999:
        return None, True

    return scrape(ptype, lowerpointrange, higherpointrange), False

# actual bot
@client.event
async def on_message(message):
    id = client.get_guild(662421888710213636)

    if str(message.author) != "Dmoj Bot#9919":
        if message.content.find("&d") != -1 and "help" in str(message.content).lower():
            await message.channel.send("Please Enter:\n &d (problem type(s))-(lowest point value)-(highest point value)\n -> to skip a category, leave it blank")

        elif message.content.find("&d") != -1:
            if "add" in str(message.content):
                badchannels.remove(str(message.channel))
                await message.channel.send("Dmojbot added to #"+str(message.channel))

            elif "remove" in str(message.content):
                badchannels.append(str(message.channel))
                await message.channel.send("Dmojbot removed from #"+str(message.channel))

            else:
                if str(message.channel) not in badchannels:
                    out = do(str(message.content))
                    if out[1]:
                        bad = True
                        await message.channel.send("ur bad\nPlease type: '&d help' for help")

                    elif not out[1]:
                        await message.channel.send(out[0])


client.run(token)
