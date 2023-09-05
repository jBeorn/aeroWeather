import discord
from discord.ext import commands
from discord import app_commands
import datetime
import aiohttp
import json


# https://beta.aviationweather.gov/data/example/

# Set to True if you want the METAR or TAF to be dumped in to a json file.
dump = False

class AeroWeather(commands.Cog):
    def __init__(self, client: commands.Bot):
        self.client = client
        print("Aero Weather Cog loaded")


    async def fetchMETAR(self, airport: str):
        async with aiohttp.ClientSession() as session:
            async with session.get(url = "https://beta.aviationweather.gov/cgi-bin/data/metar.php", params = {"ids": airport, "format": "json"}) as response:
                responseOk = response.ok
                responseStatus = response.status
                responseData = await response.json()
        if dump:
            with open("aviationWeather.json", "w") as f:
                json.dump(responseData, f, indent = 4)
        if len(responseData) == 0 or not responseOk:
            print(f"Response status - {responseStatus}, data {responseData}")
            weatherEmbed = discord.Embed(title = "Airport Not Found", color = discord.Color.blue())
            weatherEmbed.add_field(name = "", value = "Oops!! Airport not found", inline = True)
        else:
            try:
                weatherCurrent = responseData[0]
                cloudCoverage = ""
                if len(weatherCurrent["clouds"]) == 1 and weatherCurrent["clouds"][0]["cover"] in ["CLR", "CAVOK"]:
                    cloudCoverage += responseData[0]["clouds"][0]['cover']
                else:
                    for coverage in weatherCurrent["clouds"]:
                        cloudCoverage += f"{coverage['cover']} at {coverage['base']}ft \n"
                    cloudCoverage = cloudCoverage[:-2]
                weatherEmbed = discord.Embed(
                    title = f":earth_americas: {weatherCurrent['icaoId']}, {weatherCurrent['name']}", 
                    description = f":globe_with_meridians: {weatherCurrent['lat']}, {weatherCurrent['lon']} elevation __{weatherCurrent['elev']}ft__\n \n \
                        ***Zulu Time***   :calendar_spiral: {datetime.datetime.strptime(str(datetime.datetime.utcnow().replace(microsecond=0).isoformat(' ')), '%Y-%m-%d %H:%M:%S%f').strftime('%Y-%m-%d 🕐 %H%MZ')}", 
                    color = discord.Color.blue()
                    )
                weatherEmbed.add_field(name = f"{weatherCurrent['metarType']}", value = f"{weatherCurrent['metarType']} {weatherCurrent['rawOb']}", inline = False)
                weatherEmbed.add_field(name = "🎏 Winds From", value = f"{weatherCurrent['wdir']}°")
                weatherEmbed.add_field(name = "💨 Wind Speed", value = f"{weatherCurrent['wspd']} Knots")
                weatherEmbed.add_field(name = "👁️ Visibility", value = f"{weatherCurrent['visib']}ST")
                weatherEmbed.add_field(name = "☁️ Clouds", value = cloudCoverage, inline = False)
                weatherEmbed.add_field(name = "🌡️ Temperature", value = f"{weatherCurrent['temp']}°C")
                weatherEmbed.add_field(name = "💦 Dew Point", value = f"{weatherCurrent['dewp']}°C")
                weatherEmbed.add_field(name = "⏲ Sea Level Pressure", value = f"{weatherCurrent['altim']}mb")
                weatherEmbed.set_footer(text = "by beta.aviationweather.gov")
            except KeyError:
                weatherEmbed = discord.Embed(title = "No response", color = discord.Color.blue())
                weatherEmbed.add_field(name = "Error", value = "Oops!! error while parsing", inline = True)
        return weatherEmbed


    async def fetchTAF(self, airport: str):
        async with aiohttp.ClientSession() as session:
            async with session.get(url = "https://beta.aviationweather.gov/cgi-bin/data/taf.php", params = {"ids": airport, "format": "json"}) as response:
                responseOk = response.ok
                responseStatus = response.status
                responseData = await response.json()
        if dump:
            with open("aviationWeather.json", "w") as f:
                json.dump(responseData, f, indent = 4)
        if len(responseData) == 0 or not responseOk:
            print(f"Response status - {responseStatus}, data {responseData}")
            weatherEmbed = discord.Embed(title = "Airport Not Found", color = discord.Color.blue())
            weatherEmbed.add_field(name = "", value = "Oops!! Airport not found", inline = True)
        else:
            try:
                weatherCurrent = responseData[0]
                weatherEmbed = discord.Embed(
                    title = f":earth_americas: {weatherCurrent['icaoId']}, {weatherCurrent['name']}", 
                    description = f":globe_with_meridians: {weatherCurrent['lat']}, {weatherCurrent['lon']} elevation __{weatherCurrent['elev']}ft__\n \n \
                        ***Zulu Time***   :calendar_spiral: {datetime.datetime.strptime(str(datetime.datetime.utcnow().replace(microsecond=0).isoformat(' ')), '%Y-%m-%d %H:%M:%S%f').strftime('%Y-%m-%d 🕐 %H%MZ')}", 
                    color = discord.Color.blue()
                    )
                weatherEmbed.add_field(name = "TAF", value = f"{weatherCurrent['rawTAF']}", inline = False)
                weatherEmbed.set_footer(text = "by beta.aviationweather.gov")
            except KeyError:
                weatherEmbed = discord.Embed(title = "No response", color = discord.Color.blue())
                weatherEmbed.add_field(name = "Error", value = "Oops!! error while parsing", inline = True)
        return weatherEmbed


    @app_commands.command(name = "metar", description = "Get METAR by airport ICAO code")
    async def getMETAR(self, interaction: discord.Interaction, airport: app_commands.Range[str, 4, 4]):
        result = await self.fetchMETAR(airport.upper())
        await interaction.response.send_message(embed = result)


    @app_commands.command(name = "taf", description = "Get TAF by airport ICAO code")
    async def getTAF(self, interaction: discord.Interaction, airport: app_commands.Range[str, 4, 4]):
        result = await self.fetchTAF(airport.upper())
        await interaction.response.send_message(embed = result)


async def setup(client: commands.Bot) -> None:
    await client.add_cog(AeroWeather(client))