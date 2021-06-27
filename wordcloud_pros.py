import discord
from wordcloud import WordCloud
from matplotlib import pyplot as plt
import matplotlib.colors as mcolors
import japanize_matplotlib
import neologdn
import networkx as nx
import numpy as np
from wakame.tokenizer import Tokenizer
from wakame.analyzer import Analyzer
from wakame.charfilter import UnicodeNormalizeCharFilter, RegexReplaceCharFilter,CharFilter
from wakame.tokenfilter import POSKeepFilter,LowerCaseFilter
from itertools import combinations, dropwhile,chain,permutations
from collections import Counter
import io 
from datetime import datetime, timezone, timedelta
import re
import requests
from graphviz import Graph
from PIL import Image,ImageDraw
import random
import MeCab

tokenizer = Tokenizer(use_neologd=True)
class C:
    def __init__(self):
        self.x = 0

    def __call__(self):
        self.x += 1
        return print(f'🟢コマンド受け取り{self.x}回目、投稿完了🟢')
    
    @staticmethod
    def initial(ctx):
        return print(f'🟥{ctx.author.name}がcoコマンドを入力しました。🟥{datetime.now()}') 
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
            self.memnames.append('bot以外の全員')

        print(f'🟥コマンド入力結果:{vars(self)}🟥')
        
  
    def is_int(self,s):
        try:
            int(s)
        except:
            return False
        return int(s)


    def _stopword(self,arg):            
        if arg.find('rm=') == 0:
            stopword = arg.replace('-','')  
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
            self.t_msg = f'⏰過去{tdelta.days}日{h}時間{m}分の書き込み⏰'

    def _allch(self,arg):
        if arg.find('=allch') ==0:
            for ch in self.ctx.guild.text_channels:
                print(ch)
                self.chs.append(ch)

# コマンドをもとに必要情報の入手　(メッセージ取得、ギルドメンバー取得)
class Getmsg:
    def __init__(self,ch_historylist ,member):
        # メッセージのリスト
        self.list = []
        # 全メッセージ数
        self.allmsg_count = 0
        #　抽出するメッセージ数
        self.count = 0
        for each_history in ch_historylist:
            #ctxsから各投稿のメッセージ本文のみ抽出しリスト化
            for msg_info in each_history:
                msg = msg_info.content
                msg_author = msg_info.author
                self.allmsg_count += 1
                # メッセージが空文の場合抽出しない(エラー防止)
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

        print(f'🔻リストアップしたメッセージ:\n {self.list}')
        print(f'🔻リストアップしたメッセージ数:\n {self.count}')

#　janome形態素分析対策。絵文字をランダムに作成した固有名詞に変換
class ReplaceEmoji:
    @staticmethod
    def make_dict(ctx):
        emojituple =  ( ( str(elem),str(elem.url) )  for elem in ctx.guild.emojis )  
        keylist = ['凮','㪨','偁','穪','總','瀯','礹','䛒','貋']
        keys = (''.join(H) for H in permutations(keylist, 3) )
        emojidict = dict(zip(keys,emojituple))
        print(emojidict)
        return emojidict


# discordユーザー絵文字をそのままjanomeに取り込むと形態素分析で分解されてしまう。janome.CharFilterを継承して工夫する。
class EmojiCharFilter(CharFilter):
    def __init__(self,emojidict):
        self.emojidict = emojidict

    def apply(self, text):
        for k,v in self.emojidict.items():
            text = re.sub(v[0],k, text) 
        return text

class NeologdnCharFilter(CharFilter):
    def apply(self, text):
        neologdn.normalize(text)
        return text


# ワードの取得、形態素分析
class SetJanome:
    def __init__(self,msglist):
        self.msglist = msglist

    def getwords (self):
        # Janomeアナライザーの設定   
        a = Analyzer(char_filters=self.char_filters, tokenizer=tokenizer, token_filters=self.token_filters)
        # 多次元リスト　メッセージごとのワードリストを内包
        self.wordlistlist = []
        for msg in self.msglist:
            tokens = a.analyze(msg)
            w_list=[]
            # 基本形で取得する.base_formを利用
            for token in tokens:
                word = token.base_form
                part = token.part_of_speech.split(',')
                if part[1] in self.wordclass2 and not word in self.stopwordslist:
                    w_list.append(word)
            self.wordlistlist.append(w_list)
            w_list.clear
        print(f'🟥書き込みごとのワードリスト🟥{self.wordlistlist}')
        if self.wordlistlist:
            return self.wordlistlist

class WCJanome(SetJanome):
    def pros(self,stopwords=False,emojidict={}):
        self.stopwordslist = ['する']
        if stopwords:
            stopwords.extend(self.stopwordslist)
        self.char_filters = [ UnicodeNormalizeCharFilter(),EmojiCharFilter(emojidict),RegexReplaceCharFilter(r"https?://[\w!\?/\+\-_~=;\.,\*&@#\$%\(\)'\[\]]|[!#$%&'()\*\+\-\.,\/:;<=>?@\[\\\]^_`{|}~]",''),NeologdnCharFilter()]
        self.wordclass2 = ['自立','サ変接続','一般','固有名詞']
        self.token_filters = [POSKeepFilter(['名詞','形容詞']), LowerCaseFilter()]
        return self.getwords()

class CNJanome(SetJanome):
    def pros(self,stopwords=False,emojidict={}):
        self.stopwordslist = ['する']
        if stopwords:
            stopwords.extend(self.stopwordslist)
        self.char_filters = [UnicodeNormalizeCharFilter(), EmojiCharFilter(emojidict),RegexReplaceCharFilter(r"https?://[\w!\?/\+\-_~=;\.,\*&@#\$%\(\)'\[\]]|[!#$%&'()\*\+\-\.,\/:;<=>?@\[\\\]^_`{|}~]",''),NeologdnCharFilter()]
        self.wordclass2 = ['自立','サ変接続','一般','固有名詞']
        self.token_filters = [POSKeepFilter(['名詞','動詞','形容詞']), LowerCaseFilter()]               
        return self.getwords()


class MakeWordCloud:
    def __init__(self,wordlistlist,emojidict={}):
        self.wordlistlist = wordlistlist
        self.emojidict = emojidict

    #ワードクラウド前処理
    def proc(self):
        # 多次元リストのwordlistlistを平坦化
        w_list = chain.from_iterable(self.wordlistlist)
        # Counterを使用して頻出単語順でソート。70単語までに限定する。
        # wordcloud.pyのmaxwordを使わずここでやる理由は、wordcloud.pyに渡す辞書に絵文字が含まれていない為.
        c = Counter(w_list)
        self.with_emoji  = dict(c.most_common(60))
        # 絵文字タグ抜きの辞書の雛形
        self.without_emoji = self.with_emoji
        # マスク画像の作成
        self.mask_img = Image.new('RGB', (800, 500), (128, 128, 128))
        draw = ImageDraw.Draw(self.mask_img)
        #四角形の座標辞書(キー:画像url,値:[左上xy座標,描写サイズ])
        self.emoji_xy = {}
        for elem in list(self.with_emoji):
            if elem in self.emojidict.keys():
                # 絵文字サイズを絵文字出現回数で決める
                # 160を最大サイズとする
                left_x,left_y = random.randint(0,800-160),random.randint(0,500-160)
                right_x,right_y = left_x+min(self.with_emoji[elem]*60,160),left_y+min(self.with_emoji[elem]*60,160)
                # [左上のx座標, 左上のy座標, 右下のx座標, 右下のy座標]
                xylist = [left_x,left_y,right_x,right_y]
                # 絵文字スペースを白色で描写
                draw.rectangle(xylist, fill=(255,255,255))
                # emoji_xy辞書に情報追加
                url = self.emojidict[elem][1]
                self.emoji_xy[url] = xylist
                # without_emojiから絵文字タグを抜く
                del self.without_emoji[elem]
        if self.without_emoji:
            return self.wordcloud()
        else:
            return self.onlyemoji()

    # matplotlibで自作カラーフィルタを作成し、wordcloudに取り込ませる
    def wordcolor(self,word,font_size,**kwargs):
        colorlist = ['#577785','#5B2446']
        originalcm = mcolors.LinearSegmentedColormap.from_list('wordcolor', colorlist)
        color = originalcm(int(font_size))
        return mcolors.to_hex(color)

    # ワードクラウド画像作成
    def wordcloud(self):
        #color_func=self.wordcolor,
        #font_path='SourceHanSansHW-Regular.otf',

        W = WordCloud(height = 480, width = 800,min_font_size=20,font_path="/Users/itogo/Library/Fonts/SourceHanSansHW-Regular.otf",background_color="white",mask=np.array(self.mask_img),prefer_horizontal=1).generate_from_frequencies(self.without_emoji)
        plt.figure( figsize=(80,50) )
        plt.imshow(W)
        plt.axis('off')
        # 画像をメモリ上に一時保存
        self.pre_img = io.BytesIO()
        plt.savefig(self.pre_img, format='png', bbox_inches="tight") 
        plt.close()
        self.mask_img.close()

        if self.emoji_xy:
            return self.with_emoji_postproc()
        else:
            return self.without_emoji_postproc()

    # 絵文字抜きの辞書が空の場合wordcloud.pyにそのまま渡すとエラーが出る。
    def onlyemoji(self):
        self.mask_img.close()
        pre_img = Image.new('RGB', (800, 500), (255,255,255) )
        plt.axis('off')
        plt.imshow(pre_img)
        self.pre_img = io.BytesIO()
        plt.savefig(self.pre_img, format='png', bbox_inches="tight") 
        plt.close()
        pre_img.close()
        return self.with_emoji_postproc()
        
    # 作成したワードクラウドの後処理
    def with_emoji_postproc(self):
        self.pre_img.seek(0)
        wc_img = Image.open(self.pre_img,mode='r')
        for url,xylist in self.emoji_xy.items():
            print(f'🟥{url},{xylist}')
            emoji_img = Image.open(requests.get(url, stream=True).raw)
            # 絵文字の座標とサイズをマスク画像と合わせる
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
    
    # 絵文字が含まれていない場合、そのまま処理
    def without_emoji_postproc(self):   
        self.pre_img.seek(0)
        pngimage = discord.File(self.pre_img,filename = f'discord_wordcloud.png')
        self.pre_img.close()
        return pngimage

class MakeCoNet:
    # 共起ネットワーク図作成
    def __init__(self,wordlistlist,focus=False,emojidict={},getmsg_count=0):
        self.focus = focus
        self.emojidict = emojidict
        self.getmsg_count = getmsg_count
        self.wordlistlist = wordlistlist

    def makenet(self):
        pair_all = []
        for co_pair in self.wordlistlist:
            # 章ごとに単語ペアを作成
            # combinationsを使うと順番が違うだけのペアは重複しない
            # ただし、同単語のペアは存在しえるのでsetでユニークにする
            pair_l = list(combinations(set(co_pair), 2))
            # 単語ペアの順番をソート
            for i,pair in enumerate(pair_l):
                pair_l[i] = tuple(sorted(pair)) 
            pair_all += pair_l
        # 単語ペアごとの出現章数
        pair_count = Counter(pair_all)
        # 🔻ペアが少なすぎるペアは除く。        
        if self.getmsg_count <= 100 or self.focus: # 取得メッセージ数が100未満の場合及びfocusが設定された場合は除かない
            mn_cnt = 1
        else: # focusが設定されていない場合：取得するメッセージ数*0.001で調整
            mn_cnt = round(2+(self.getmsg_count *0.001))
        #　dropwhile：条件が成立しているうちは読み飛ばし、不成立になったらそこからリスト作成
        for key, count in dropwhile(lambda key_count: key_count[1] >= mn_cnt, pair_count.most_common()):
            del pair_count[key]
        # 単語ごとの出現章数
        word_count = Counter()
        for co_pair in self.wordlistlist:
            word_count += Counter(set(co_pair))
        # 単語ペアごとのjaccard係数を計算
        jaccard_coef = []
        for pair, cnt in pair_count.items():
            jaccard_coef.append(cnt / (word_count[pair[0]] + word_count[pair[1]] - cnt))
        o_jaccard_dict = {}
        for (pair, cnt), coef in zip(pair_count.items(), jaccard_coef):
            o_jaccard_dict[pair] = coef
            print(f'ペア{pair}, 出現回数{cnt}, 係数{coef}, ワード1出現数{word_count[pair[0]]}, ワード2出現数{word_count[pair[1]]}')  
        # o_jaccard_dictをjaccard係数降順にソートしjaccard係数トップ90を取り出し 
        if not self.focus:
            self.jaccard_dict = dict(sorted(o_jaccard_dict.items(), key=lambda x: x[1], reverse=True)[0:69]) 
        else:
        # focusの場合は取り出さない
            self.jaccard_dict = o_jaccard_dict
        print(f'🟥jaccard_dict🟥 {self.jaccard_dict}')
        return self.build_network()

    def build_network(self):
        if not self.jaccard_dict:
            return 'No_dict'
        # networkxで計算
        G = nx.Graph()
        # 接点／単語（node）の追加
        nodes = set([j for pair in self.jaccard_dict.keys() for j in pair])
        G.add_nodes_from(nodes)
        # 線（edge）の追加
        for pair, coef in self.jaccard_dict.items():
            G.add_edge(pair[0], pair[1], weight=coef) 
        # focusの場合
        if self.focus :
            try:
                keepnodes = list((G[self.focus]).keys())
            except KeyError:
                return 'No_focus'
            else:
                keepnodes = list((G[self.focus]).keys())
                keepnodes.append(self.focus)
                print(f'🟦{keepnodes}')
                #ノード削除
                rm_nodes = set(nodes) ^ set(keepnodes)
                G.remove_nodes_from(rm_nodes)
                G.remove_nodes_from(list(nx.isolates(G)))
        print('Number of nodes =', G.number_of_nodes())
        print('Number of edges =', G.number_of_edges())
        #　graphviz.pyで描写
        g = Graph(engine='neato')
        g.attr(overlap='false') 
        g.attr(size='800,500')
        g.attr(outputorder="edgesfirst")
        #　networkxのpagerankを活用して色やノードサイズを変化させる
        pagerank = nx.pagerank(G)
        print(pagerank)
        cm = plt.get_cmap('rainbow')
        for node,rank in pagerank.items():
            ncm =cm(rank*15)
            colorhex = mcolors.to_hex(ncm)
            if node in self.emojidict.keys():
                '''
                FIX ME!!!!!
                g.attr('node', shape='circle',color=str(colorhex),style='filled', fixedsize='True',height=20,imagescale='both',margin=' 0.001,0.001')
                emojivalue = self.emojidict[node]
                emoji_img = Image.open(requests.get(emojivalue[1], stream=True).raw)
                bytes = io.BytesIO()    
                emoji_img.save(bytes, format='PNG')
                g.node(bytes)
                bytes.close()
                '''
                pass 
            else:
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