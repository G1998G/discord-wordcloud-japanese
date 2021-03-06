import discord
from wordcloud import WordCloud
from matplotlib import pyplot as plt
import matplotlib.colors as mcolors
import japanize_matplotlib
import neologdn
import networkx as nx
import numpy as np
import MeCab
from wakame.tokenizer import Tokenizer
from wakame.analyzer import Analyzer
from wakame.charfilter import UnicodeNormalizeCharFilter, RegexReplaceCharFilter,CharFilter
from wakame.tokenfilter import POSKeepFilter,LowerCaseFilter
from itertools import combinations, dropwhile,chain
from collections import Counter
import io 
from datetime import datetime, timezone, timedelta
import re
import requests
from graphviz import Graph
from PIL import Image,ImageDraw
import random


tokenizer = Tokenizer(use_neologd=True)
class C:
    def __init__(self):
        self.x = 0

    def __call__(self):
        self.x += 1
        return print(f'ð¢ã³ãã³ãåãåã{self.x}åç®ãæç¨¿å®äºð¢')
    
    @staticmethod
    def initial(ctx):
        return print(f'ð¥{ctx.author.name}ãcoã³ãã³ããå¥åãã¾ãããð¥{datetime.now()}') 
postc = C()
class SetCmd1:
    def __init__ (self,ctx,args):
        self.ctx = ctx
        self.now = datetime.now(timezone.utc)
        self.dt = datetime.now(timezone.utc)
        self.maxnum = 10000
        self.countnum = 1000
        self.time = False
        self.t_msg = False
        self.chs = []
        self.chnames = []
        self.mems = []
        self.memnames = []
        self.stopwords = []
        self.focus = False

        if args:
            for arg in args:
                if type(arg) is int:
                    self.countnum = arg    
                elif type(arg) is discord.Member:
                    self.mems.append(arg)
                    self.memnames.append(arg.name)
                elif type(arg) is discord.TextChannel:
                    self.chs.append(arg)
                    self.chnames.append(arg.name)
                elif type(arg) is str:
                    self._stopword(arg)
                    self._focus(arg)
                    self._time(arg)
                    self._allch(arg)
        
        if not self.chs and not self.chnames:
            self.chs.append(ctx.channel)
            self.chnames.append(ctx.channel.name)
        if not self.memnames:
            self.memnames.append('botä»¥å¤ã®å¨å¡')

        print(f'ð¥ã³ãã³ãå¥åçµæ:{vars(self)}ð¥')
        
  
    def is_int(self,s):
        try:
            int(s)
        except:
            return False
        return int(s)


    def _stopword(self,arg):            
        if arg.find('rm=') == 0:
            stopword = arg.replace('rm-','')  
            self.stopwords.append(stopword)

    def _focus(self,arg):
        if arg.find('focus=') == 0:
            self.focus = arg.replace('focus=','')

    def _time(self,arg):
        if self.is_int(arg[2:]):  
            if arg.find('d=') ==0:

                self.dt -= timedelta(days=int(arg[2:]))
            elif arg.find('h=') ==0:
                self.dt -= timedelta(hours=int(arg[2:]))
            elif arg.find('m=') ==0:
                self.dt -= timedelta(minutes=int(arg[2:]))
            else:
                return None
            tlist = ['%Y','%m','%d','%H','%M']
            dtlist = []
            for elem in tlist:
                dtlist.append(self.dt.strftime(elem))
            self.time = datetime(int(dtlist[0]),int(dtlist[1]),int(dtlist[2]),int(dtlist[3]),int(dtlist[4]), second=0, microsecond=0, tzinfo=None)
            tdelta = abs(self.now-self.dt)
            m, s = divmod(tdelta.seconds, 60)
            h, m = divmod(m, 60)
            self.t_msg = f'â°éå»{tdelta.days}æ¥{h}æé{m}åã®æ¸ãè¾¼ã¿â°'

    def _allch(self,arg):
        if arg.find('=allch') ==0:
            for ch in self.ctx.guild.text_channels:
                print(ch)
                self.chs.append(ch)

# ã³ãã³ãããã¨ã«å¿è¦æå ±ã®å¥æã(ã¡ãã»ã¼ã¸åå¾ãã®ã«ãã¡ã³ãã¼åå¾)
class Getmsg:
    def __init__(self,ch_historylist ,member):
        # ã¡ãã»ã¼ã¸ã®ãªã¹ã
        self.list = []
        # å¨ã¡ãã»ã¼ã¸æ°
        self.allmsg_count = 0
        #ãæ½åºããã¡ãã»ã¼ã¸æ°
        self.count = 0
        for each_history in ch_historylist:
            #ctxsããåæç¨¿ã®ã¡ãã»ã¼ã¸æ¬æã®ã¿æ½åºããªã¹ãå
            for msg_info in each_history:
                msg = msg_info.content
                msg_author = msg_info.author
                self.allmsg_count += 1
                # ã¡ãã»ã¼ã¸ãç©ºæã®å ´åæ½åºããªã(ã¨ã©ã¼é²æ­¢)
                if not msg: 
                    continue
                elif msg_author.bot:
                    continue
                elif not member:
                    self.list.append(msg)
                    self.count += 1
                elif member:
                    if msg_author in member:
                        self.list.append(msg)
                        self.count += 1

        print(f'ð»ãªã¹ãã¢ããããã¡ãã»ã¼ã¸:\n {self.list}')
        print(f'ð»ãªã¹ãã¢ããããã¡ãã»ã¼ã¸æ°:\n {self.count}')

#ãjanomeå½¢æç´ åæå¯¾ç­ãçµµæå­ãã©ã³ãã ã«ä½æããåºæåè©ã«å¤æ
class ReplaceEmoji:
    @staticmethod
    def make_dict(ctx):
        emojidict = dict()
        for elem in ctx.guild.emojis:
            emojidict[str(elem)] = str(elem.url)

        print(emojidict)
        return emojidict


# discordã¦ã¼ã¶ã¼çµµæå­ããã®ã¾ã¾janomeã«åãè¾¼ãã¨å½¢æç´ åæã§åè§£ããã¦ãã¾ããjanome.CharFilterãç¶æ¿ãã¦å·¥å¤«ããã
class EmojiCountFilter():
    def __init__(self,emojidict):
        self.emojidict = emojidict
        self.emojilist = list()

    def apply(self, text):
        for k in self.emojidict.keys():
            if re.search(k,text):
                self.emojilist.append(k)
                text = re.sub(k,"",text)
        return text

class NeologdnCharFilter(CharFilter):
    def apply(self, text):
        neologdn.normalize(text, tilde="remove")
        return text


# ã¯ã¼ãã®åå¾ãå½¢æç´ åæ
class SetJanome:
    def __init__(self,msglist,emojidict=dict(),stopwords=False):
        self.msglist = msglist
        self.emojidict = emojidict
        self.stopwords = stopwords
        # å¤æ¬¡åãªã¹ããã¡ãã»ã¼ã¸ãã¨ã®ã¯ã¼ããªã¹ããåå
        

    def getwords (self):
        self.wordlistlist = []
        # EmojiCountFilterãèµ·å
        emojifilter = EmojiCountFilter(self.emojidict)
        # Janomeã¢ãã©ã¤ã¶ã¼ã®è¨­å®&èµ·å   
        a = Analyzer(char_filters=self.char_filters, tokenizer=tokenizer, token_filters=self.token_filters)
        for msg in self.msglist:
            msg = emojifilter.apply(msg)
            if not msg:
                pass
            else:
                tokens = a.analyze(msg)
                w_list=[]
                # åºæ¬å½¢ã§åå¾ãã.base_formãå©ç¨
                for token in tokens:
                    word = token.base_form
                    part = token.part_of_speech.split(',')
                    if part[1] in self.wordclass2 and not word in self.stopwordslist:
                        w_list.append(word)
                self.wordlistlist.append(w_list)
                w_list.clear

        self.emojilist = emojifilter.emojilist
        print(self.emojilist)
        print(f'ð¥æ¸ãè¾¼ã¿ãã¨ã®ã¯ã¼ããªã¹ãð¥{self.wordlistlist}')
        return self.wordlistlist

class WCJanome(SetJanome):
    def pros(self):
        self.stopwordslist = ['ãã']
        if self.stopwords:
            self.stopwords.extend(self.stopwordslist)
        self.char_filters = [ UnicodeNormalizeCharFilter(),RegexReplaceCharFilter(r"https?://[\w!\?/\+\-_~=;\.,\*&@#\$%\(\)'\[\]]|[!#$%&'()\*\+\-\.,\/:;<=>?@\[\\\]^_`{|}~]",''),NeologdnCharFilter()]
        self.wordclass2 = ['èªç«','ãµå¤æ¥ç¶','ä¸è¬','åºæåè©']
        self.token_filters = [POSKeepFilter(['åè©','å½¢å®¹è©']), LowerCaseFilter()]
        return self.getwords()

class CNJanome(SetJanome):
    def pros(self):
        self.stopwordslist = ['ãã']
        if self.stopwords:
            self.stopwords.extend(self.stopwordslist)
        self.char_filters = [UnicodeNormalizeCharFilter(),RegexReplaceCharFilter(r"https?://[\w!\?/\+\-_~=;\.,\*&@#\$%\(\)'\[\]]|[!#$%&'()\*\+\-\.,\/:;<=>?@\[\\\]^_`{|}~]",''),NeologdnCharFilter()]
        self.wordclass2 = ['èªç«','ãµå¤æ¥ç¶','ä¸è¬','åºæåè©']
        self.token_filters = [POSKeepFilter(['åè©','åè©','å½¢å®¹è©']), LowerCaseFilter()]               
        return self.getwords()


class MakeWordCloud:
    def __init__( self,wordlistlist,emojidict={},emojilist=[] ):
        self.wordlistlist = wordlistlist
        self.emojidict = emojidict
        self.emojilist = emojilist

    #ã¯ã¼ãã¯ã©ã¦ãåå¦ç
    def proc(self):
        # å¤æ¬¡åãªã¹ãã®wordlistlistãå¹³å¦å
        w_list = chain.from_iterable(self.wordlistlist)
        # Counterãä½¿ç¨ãã¦é »åºåèªé ã§ã½ã¼ãã70åèªã¾ã§ã«éå®ããã
        # wordcloud.pyã®maxwordãä½¿ããããã§ããçç±ã¯ãwordcloud.pyã«æ¸¡ãè¾æ¸ã«çµµæå­ãå«ã¾ãã¦ããªãçº.
        w_count = Counter(w_list)
        self.w_count_dict  = dict(w_count.most_common(50))
        e_count = Counter(self.emojilist)
        e_count_dict = dict(e_count.most_common(4))
        print(self.w_count_dict)

        self.emoji_xy = {}
        if e_count_dict:
            # ãã¹ã¯ç»åã®ä½æ
            self.base_img = Image.new('RGB', (800, 500), (128, 128, 128))
            draw = ImageDraw.Draw(self.base_img)
           
            for k,c in e_count_dict.items():
                # çµµæå­ãµã¤ãºãçµµæå­åºç¾åæ°ã§æ±ºãã
                # 160ãæå¤§ãµã¤ãºã¨ãã
                left_x,left_y = random.randint(0,800-160),random.randint(0,500-160)
                right_x,right_y = left_x+min(c*60,160),left_y+min(c*60,160)
                # [å·¦ä¸ã®xåº§æ¨, å·¦ä¸ã®yåº§æ¨, å³ä¸ã®xåº§æ¨, å³ä¸ã®yåº§æ¨]
                xylist = [left_x,left_y,right_x,right_y]
                # çµµæå­ã¹ãã¼ã¹ãç½è²ã§æå
                draw.rectangle(xylist, fill=(255,255,255))
                # emoji_xyè¾æ¸ã«æå ±è¿½å 
                url = self.emojidict[k]
                self.emoji_xy[url] = xylist
            if self.w_count_dict:
                print('çµµæå­ããã¯ã¼ããã')
                return self.wordcloud()
            else:
                print('çµµæå­ã®ã¿ãã')
                self.pre_img = self.base_img
                return self.with_emoji_postproc()
        
        elif self.w_count_dict.items():
            print('çµµæå­ãªãã¯ã¼ããã')
            self.base_img = Image.new('RGB', (800, 500), (128,128,128) )
            return self.wordcloud()
        else:
            return False

    # matplotlibã§èªä½ã«ã©ã¼ãã£ã«ã¿ãä½æããwordcloudã«åãè¾¼ã¾ãã
    def wordcolor(self,word,font_size,**kwargs):
        colorlist = ['#577785','#5B2446']
        originalcm = mcolors.LinearSegmentedColormap.from_list('wordcolor', colorlist)
        color = originalcm(int(font_size))
        return mcolors.to_hex(color)

    # ã¯ã¼ãã¯ã©ã¦ãç»åä½æ
    def wordcloud(self):
        #color_func=self.wordcolor,
        #font_path='SourceHanSansHW-Regular.otf',

        W = WordCloud(height = 480, width = 800,min_font_size=20,font_path="/Users/itogo/Library/Fonts/SourceHanSansHW-Regular.otf",background_color="white",mask=np.array(self.base_img),prefer_horizontal=1).generate_from_frequencies(self.w_count_dict)
        plt.figure( figsize=(80,50) )
        plt.imshow(W)
        plt.axis('off')
        # ç»åãã¡ã¢ãªä¸ã«ä¸æä¿å­
        self.pre_img = io.BytesIO()
        plt.savefig(self.pre_img, format='png', bbox_inches="tight") 
        plt.close()
        self.base_img.close()
        if self.emoji_xy:
            return self.with_emoji_postproc()
        else:
            return self.without_emoji_postproc()
        
    # ä½æããã¯ã¼ãã¯ã©ã¦ãã®å¾å¦ç
    def with_emoji_postproc(self):
        self.pre_img.seek(0)
        wc_img = Image.open(self.pre_img,mode='r')
        for url,xylist in self.emoji_xy.items():
            print(f'ð¥{url},{xylist}')
            emoji_img = Image.open(requests.get(url, stream=True).raw)
            # çµµæå­ã®åº§æ¨ã¨ãµã¤ãºããã¹ã¯ç»åã¨åããã
            left_x = int(wc_img.width*(xylist[0]/800))
            left_y = int(wc_img.height*(xylist[1]/500))
            right_y = int(wc_img.height*(xylist[3]/500))
            imgsize = abs(left_y-right_y)
            emoji_img = emoji_img.resize((imgsize, imgsize))
            wc_img.paste(emoji_img, (left_x,left_y),emoji_img)
        wc_bytes = io.BytesIO()    
        wc_img.save(wc_bytes, format='PNG')
        wc_bytes.seek(0)
        pngimage = discord.File(wc_bytes,filename = f'discord_wordcloud.png')
        wc_bytes.close()
        self.pre_img.close()
        return pngimage
    
    # çµµæå­ãå«ã¾ãã¦ããªãå ´åããã®ã¾ã¾å¦ç
    def without_emoji_postproc(self):   
        self.pre_img.seek(0)
        pngimage = discord.File(self.pre_img,filename = f'discord_wordcloud.png')
        self.pre_img.close()
        return pngimage

class MakeCoNet:
    # å±èµ·ãããã¯ã¼ã¯å³ä½æ
    def __init__(self,wordlistlist,focus=False,getmsg_count=0):
        self.focus = focus
        self.getmsg_count = getmsg_count
        self.wordlistlist = wordlistlist

    def makenet(self):
        pair_all = []
        for co_pair in self.wordlistlist:
            # ç« ãã¨ã«åèªãã¢ãä½æ
            # combinationsãä½¿ãã¨é çªãéãã ãã®ãã¢ã¯éè¤ããªã
            # ãã ããååèªã®ãã¢ã¯å­å¨ãããã®ã§setã§ã¦ãã¼ã¯ã«ãã
            pair_l = list(combinations(set(co_pair), 2))
            # åèªãã¢ã®é çªãã½ã¼ã
            for i,pair in enumerate(pair_l):
                pair_l[i] = tuple(sorted(pair)) 
            pair_all += pair_l
        # åèªãã¢ãã¨ã®åºç¾ç« æ°
        pair_count = Counter(pair_all)
        # ð»ãã¢ãå°ãªããããã¢ã¯é¤ãã        
        if self.getmsg_count <= 100 or self.focus: # åå¾ã¡ãã»ã¼ã¸æ°ã100æªæºã®å ´ååã³focusãè¨­å®ãããå ´åã¯é¤ããªã
            mn_cnt = 1
        else: # focusãè¨­å®ããã¦ããªãå ´åï¼åå¾ããã¡ãã»ã¼ã¸æ°*0.001ã§èª¿æ´
            mn_cnt = round(2+(self.getmsg_count *0.001))
        #ãdropwhileï¼æ¡ä»¶ãæç«ãã¦ãããã¡ã¯èª­ã¿é£ã°ããä¸æç«ã«ãªã£ãããããããªã¹ãä½æ
        for key, count in dropwhile(lambda key_count: key_count[1] >= mn_cnt, pair_count.most_common()):
            del pair_count[key]
        # åèªãã¨ã®åºç¾ç« æ°
        word_count = Counter()
        for co_pair in self.wordlistlist:
            word_count += Counter(set(co_pair))
        # åèªãã¢ãã¨ã®jaccardä¿æ°ãè¨ç®
        jaccard_coef = []
        for pair, cnt in pair_count.items():
            jaccard_coef.append(cnt / (word_count[pair[0]] + word_count[pair[1]] - cnt))
        o_jaccard_dict = {}
        for (pair, cnt), coef in zip(pair_count.items(), jaccard_coef):
            o_jaccard_dict[pair] = coef
            print(f'ãã¢{pair}, åºç¾åæ°{cnt}, ä¿æ°{coef}, ã¯ã¼ã1åºç¾æ°{word_count[pair[0]]}, ã¯ã¼ã2åºç¾æ°{word_count[pair[1]]}')  
        # o_jaccard_dictãjaccardä¿æ°éé ã«ã½ã¼ããjaccardä¿æ°ããã90ãåãåºã 
        if not self.focus:
            self.jaccard_dict = dict(sorted(o_jaccard_dict.items(), key=lambda x: x[1], reverse=True)[0:69]) 
        else:
        # focusã®å ´åã¯åãåºããªã
            self.jaccard_dict = o_jaccard_dict
        print(f'ð¥jaccard_dictð¥ {self.jaccard_dict}')
        return self.build_network()

    def build_network(self):
        if not self.jaccard_dict:
            return 'No_dict'
        # networkxã§è¨ç®
        G = nx.Graph()
        # æ¥ç¹ï¼åèªï¼nodeï¼ã®è¿½å 
        nodes = set([j for pair in self.jaccard_dict.keys() for j in pair])
        G.add_nodes_from(nodes)
        # ç·ï¼edgeï¼ã®è¿½å 
        for pair, coef in self.jaccard_dict.items():
            G.add_edge(pair[0], pair[1], weight=coef) 
        # focusã®å ´å
        if self.focus :
            try:
                keepnodes = list((G[self.focus]).keys())
            except KeyError:
                return 'No_focus'
            else:
                keepnodes = list((G[self.focus]).keys())
                keepnodes.append(self.focus)
                print(f'ð¦{keepnodes}')
                #ãã¼ãåé¤
                rm_nodes = set(nodes) ^ set(keepnodes)
                G.remove_nodes_from(rm_nodes)
                G.remove_nodes_from(list(nx.isolates(G)))
        print('Number of nodes =', G.number_of_nodes())
        print('Number of edges =', G.number_of_edges())
        #ãgraphviz.pyã§æå
        g = Graph(engine='neato')
        g.attr(overlap='false') 
        g.attr(size='800,500')
        g.attr(outputorder="edgesfirst")
        #ãnetworkxã®pagerankãæ´»ç¨ãã¦è²ããã¼ããµã¤ãºãå¤åããã
        pagerank = nx.pagerank(G)
        print(pagerank)
        cm = plt.get_cmap('rainbow')
        for node,rank in pagerank.items():
            ncm =cm(rank*15)
            colorhex = mcolors.to_hex(ncm)
            g.attr('node', shape='circle',color=str(colorhex),style='filled',fontsize='22',fontname='SourceHanSansHW', fixedsize='True',height=str(len(node)/3.3 + 10*rank) )
            g.node(node)
        edges = []
        for source in G.edges(data=True):
            edges.append([source[0],source[1],source[2]['weight']])
        print(edges)
        for edge in edges:
            g.attr( 'edge',weight=str( min(edge[2]*10,30) ))
            g.edge(edge[0],edge[1])
        g.format = 'png'
        datastream = io.BytesIO(g.pipe())
        datastream.seek(0)
        pngimage = discord.File(datastream,filename = f'discord_network_graph.png')
        datastream.close()
        return pngimage