import discord_wordcloud_pros as pros
from discord.ext import commands
import discord
from typing import Union


class WordCloudCommands(commands.Cog):
    def __init__(self, bot):
        super().__init__()
        self.bot = bot
    
    async def pros_c(self,ctx,args):
        print(list(map(lambda x:type(x),args)))
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
            emojidict = pros.ReplaceEmoji.make_dict(ctx)
            res_wakame = pros.WCJanome(getmsg.list,emojidict,cmd.stopwords)
            wordlistlist = res_wakame.pros()
            print(wordlistlist)
            if not wordlistlist:
                await ctx.send(content=f'`{",".join(cmd.chnames)} の過去{getmsg.allmsg_count}回分の書き込みから{",".join(cmd.memnames)}の書き込みを調べたけど、{",".join(cmd.memnames)}の書き込みが見つからなかったよ。`')
            else:
                wc = pros.MakeWordCloud(wordlistlist=wordlistlist,emojidict=emojidict,emojilist=res_wakame.emojilist)
                graph_res = wc.proc()
                await ctx.send(file=graph_res, content=f' `{",".join(cmd.chnames)} の過去{getmsg.allmsg_count}回分の書き込みから{",".join(cmd.memnames)}の書き込みを調べたよ。\n書き込み数:{getmsg.count}回\n取り除いたワード:{",".join(cmd.stopwords)}\n期間指定：{cmd.t_msg} \n※取得期間指定が優先されるよ。`' )
        pros.postc()


    @commands.command()
    async def c(self,ctx, *args: Union[discord.TextChannel, discord.Member,int,str]):
        '''
        ワードクラウドを生成 ℹ️
        '''
        pros.C.initial(ctx)
        print(list(map(lambda x:type(x),args)))
        async with ctx.typing(): # 送られてきたチャンネルで入力中と表示させる        
            await self.pros_c(ctx,args)
    
    async def pros_dc(self,ctx,args):
        print(args)
        emojidict =pros.ReplaceEmoji.make_dict(ctx)
        res_wakame = pros.WCJanome(args)
        wordlistlist = res_wakame.pros(emojidict=emojidict)
        wc = pros.MakeWordCloud(wordlistlist)
        graph_res = wc.proc()
        await ctx.send(file=graph_res,content=f'`{ctx.author.name}さんの書き込みからそのままワードクラウドを作りました`')
        pros.postc()

    @commands.command()
    async def dc(self,ctx, *args):
        '''
        書き込みそのものからワードクラウドを生成
        '''
        pros.C.initial(ctx)
        
        async with ctx.typing(): # 送られてきたチャンネルで入力中と表示させる
            await self.pros_dc(self,ctx,*args)

async def setup(bot):
    print('ワードクラウドのcogがリロードされました')
    await bot.add_cog(WordCloudCommands(bot))
