import discord_wordcloud_pros as pros
from discord.ext import commands
import discord

class OtherCommands(commands.Cog):
    def __init__(self, bot):
        super().__init__()
        self.bot = bot
    
    async def pros_opt(self,ctx,arg):
        '''
        コマンドのオプション機能を解説表示
        '''
        pros.C.initial(ctx)
        embed= discord.Embed(title="**🔻オプション一覧🔻**", description=f"```「>w 〇〇」の形式で入力(間に必ず半角スペースを入れて下さい。)```")
        embed.add_field(name="#チャンネル", value=f"```指定されたチャンネルから取得。\n(複数指定可)```")
        embed.add_field(name="@メンション", value=f"```メンションされた人の書き込みのみから取得。\n(複数指定可)```")
        embed.add_field(name="正の整数", value=f"```書き込み取得数の指定。\n(複数指定不可)```")
        embed.add_field(name="d=正の整数", value=f"```例「d=1」:過去24時間の書き込みを取得。\n(h,mと併用可)```")
        embed.add_field(name="h=正の整数", value=f"```例「h=1」:過去1時間の書き込みを取得。\n(d,mと併用可)```")
        embed.add_field(name="m=正の整数", value=f"```例「m=1」:過去1分の書き込みを取得。\n(h,dと併用可)```")
        embed.add_field(name="rm=ワード", value=f"```例「rm=おはよう」:「おはよう」が結果から除外される。\n(複数回指定可)```")
        embed.add_field(name="focus=ワード", value=f"```例「focus=おはよう」:「おはよう」と繋がるワードのみネットワーク図として出力される。\n(複数指定不可)```")
        embed.add_field(name="allh=", value=f"```全チャンネルから書き込みを取得。各チャンネルに対して同じ設定が適用される。チャンネル数が多いとエラーになります。\n例: =allh 100 各チャンネルから100回分ずつ書き込み取得```")
        await ctx.send(embed=embed)
        pros.postc()


    @commands.command()
    async def opt(self,ctx,*args):
        await self.pros_opt(ctx,args)



    @commands.command()
    async def profile(self,ctx,*args):
        '''
        bot作成者の紹介
        '''
        pros.C.initial(ctx)
        embed= discord.Embed(title="**bot作成者**", description=f"趣味でbot等を作っています。\n [GitHubプロフィールページ](https://github.com/G1998G)")
        embed.set_thumbnail(url="https://avatars.githubusercontent.com/u/60283066?s=400&v=4")
        await ctx.send(embed=embed)
        pros.postc()

await def setup(bot):
    return bot.add_cog(OtherCommands(bot))