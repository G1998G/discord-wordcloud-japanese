from discord.ext import commands
import discord
import asyncio
class HelpCommand(commands.HelpCommand):
    def __init__(self):
        super().__init__()
        self.no_category = "HelpCommand"
        self.command_attrs["description"] = "コマンドリストを表示します。"

    async def send_bot_help(self,mapping):
        '''
        ヘルプを表示するコマンド
        '''
        content = ""
        for cog in mapping:
            # 各コグのコマンド一覧を content に追加していく
            command_list = await self.filter_commands(mapping[cog])
            if not command_list:
                # 表示できるコマンドがないので、他のコグの処理に移る
                continue
            if cog is None:
                # コグが未設定のコマンドなので、no_category属性を参照する
                content += f"\n**{self.no_category}**\n"
            else:
                content += f"\n**{cog.qualified_name}**\n"
            for command in command_list:
                content += f"{self.context.prefix}{command.name}  `{command.help}`\n"
            content += "\n"
        content += f"`ℹ️マークのついているコマンドは豊富なオプションがあります。"
        embed = discord.Embed(title="**コマンドリスト**",description=content,color=discord.Colour.dark_orange())
        await self.get_destination().send(embed=embed)

    
async def main(bot):
    await bot.load_extension("conetwork_cog")
    await bot.load_extension("wordcloud_cog")  
    await bot.load_extension("option_cog") 
    @bot.event
    async def on_ready():
        print(f'🟠ログインしました🟠')
    await bot.start( 'TOKEN')
    
if __name__ == '__main__':
    intents = discord.Intents.all()
    intents.members = True
    bot = commands.Bot(command_prefix=commands.when_mentioned_or("?"),intents=intents,help_command= HelpCommand())
    asyncio.run(main(bot))
