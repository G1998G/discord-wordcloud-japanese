import wordcloud_pros as pros
from discord.ext import commands
import discord
from typing import Union
from discord_slash import SlashCommand,cog_ext
from discord_slash.utils.manage_commands import create_option

class CoNetworkCommands(commands.Cog):
    def __init__(self, bot):
        super().__init__()
        self.bot = bot

    async def pros_n(self,ctx,args):
        cmd = pros.SetCmd1(ctx,args)
        if cmd.countnum > cmd.maxnum or cmd.countnum <= 0:
            await ctx.send('`収集できる書き込み数は0以上10000以下だよ。正の整数を入力してね。`')        
        else:
            ch_historylist = []
            if cmd.time:
                for ch in cmd.chs:
                    ch_historylist.append(await ch.history(limit = None,after = cmd.time).flatten())
            else :              
                for ch in cmd.chs:
                    ch_historylist.append(await ch.history(limit=cmd.countnum).flatten())

            getmsg = pros.Getmsg(ch_historylist,cmd.mems)
            emojidict =pros.ReplaceEmoji.make_dict(ctx)
            res_janome = pros.CNJanome(getmsg.list,emojidict,cmd.stopwords)
            wordlistlist = res_janome.pros()
            if not wordlistlist:
                await ctx.send(content=f'`{",".join(cmd.chnames)}の過去{getmsg.allmsg_count}回分の書き込みから{",".join(cmd.memnames)}の書き込みを調べたけど、書き込みが見つからなかったよ.`')
            else:
                n = pros.MakeCoNet(getmsg_count=getmsg.count,focus=cmd.focus,wordlistlist=wordlistlist)
                graph_res = n.makenet()
                if graph_res == 'No_dict':
                    await ctx.send( content=f'`該当する書き込みから共起ネットワーク図を作れなかったよ。`' )
                elif graph_res == 'No_focus':
                    await ctx.send( content=f'`フォーカスワード:{cmd.focus}で絞り込んだところ、書き込みがゼロになったよ。`' )
                else:
                    await ctx.send(file=graph_res, content=f'`{",".join(cmd.chnames)}の過去{getmsg.allmsg_count}回分の書き込みから{"".join(cmd.memnames)}の書き込みを調べたよ。\n取得できた書き込み数:{getmsg.count}回\n取り除いたワード:{",".join(cmd.stopwords)}\n絞り込み:{cmd.focus}\n期間指定{cmd.t_msg} \n※取得期間指定が優先されるよ。`' )
            pros.postc()
            return
    
    @commands.command()
    async def n(self,ctx, *args:Union[discord.TextChannel, discord.Member,int,str]):
        '''
        共起ネットワーク図を生成　ℹ️
        '''
        pros.C.initial(ctx)
        print(vars(ctx))
        print(list(map(lambda x:[type(x),x],args)))
        async with ctx.typing(): # 送られてきたチャンネルで入力中と表示させる
            await self.pros_n(ctx,args)
        

    @cog_ext.cog_slash(name="n", description="共起ネットワーク図を作成",options=[
        create_option(name="countnum", option_type=4,description="調べる書き込み数",required=False),
        create_option(name="member", option_type=6,description="メンバー指定",required=False),
        create_option(name="channel", option_type=7,description="チャンネル指定",required=False),
        create_option(name="day", option_type=4,description="遡及日",required=False),
        create_option(name="hour", option_type=4,description="遡及時間",required=False),
        create_option(name="minute", option_type=4,description="遡及分",required=False),
        create_option(name="stopword", option_type=3,description="取り除くワード",required=False),
        create_option(name="focus", option_type=3,description="絞り込むワード",required=False)
    ])
    async def n_slash(self,ctx, countnum = 5000, member = None,channel = None,day = None,hour = None,minute = None,stopword =None,focus= None):
        if day:
            day = f'd={day}'
        if hour:
            hour = f'h={hour}'
        if minute:
            minute = f'm={minute}'
        if stopword:
            stopword = f'rm={stopword}'
        if focus:
            focus = f'focus={focus}'
        print(vars(ctx))
        
        args = (countnum,member,channel,day,hour,minute,stopword,focus)
        with await ctx.defer():
            await self.pros_n(ctx,args)

    
    async def pros_dn(self,ctx,*args):
        print(args)
        emojidict =pros.ReplaceEmoji.make_dict(ctx)
        res_janome = pros.CNJanome(args)
        wordlistlist = res_janome.pros(emojidict=emojidict)
        n = pros.MakeCoNet(wordlistlist)
        graph_res = n.makenet()
        await ctx.send(file=graph_res,content=f'`{ctx.author.name}さんの書き込みからそのまま共起ネットワーク図を作りました`')
        pros.postc()
        return
        

    @commands.command()
    async def dn(self,ctx, *args):
        '''
        書き込みそのものから共起ネットワーク図を生成
        '''
        pros.C.initial(ctx)
        async with ctx.typing(): # 送られてきたチャンネルで入力中と表示させる
            await self.pros_dn(self,ctx,*args)
        

    @cog_ext.cog_slash(name="dn",description=f'本文から共起ネットワーク図を生成', options=[
        create_option(name="args", option_type=3,description="本文を入力",required=True)])
    async def dc_slash(self,ctx, args):
        await self.pros_dn(ctx,args)

def setup(bot):
    return bot.add_cog(CoNetworkCommands(bot))