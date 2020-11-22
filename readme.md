# Nozomi.la AI
The author is not affiliated to Nozomi.la. This is a third-party tool.  
作者与Nozomi.la没有从属关系。本工具是第三方工具。 
The author failed to contact Nozomi.la. If nozomi.la wants to contact the author, feel free to reach me on Github.  

Nozomi.la has netizen-created content. What you see in this tool does not represent the author's point of view.  
Nozomi.la 包含网民创作的内容，不代表本工具作者观点。 
Please be advised that errotic contents may show up. You can teach the AI to avoid errotic contents, but I cannot guarantee anything.  
请注意，具有性意味的内容可能会出现。你可以让AI避开这些内容，但我不保证你会一次也不看见。  

This tool can help you find works that you like.  
This tool also allows you to better understand your own preferences. Run summarizeTags.py to generate the report. You will be surprised.  
本工具可以助你搜集喜欢的作品，也可助你更好地理解自己的口味。时不时运行 summarizeTags.py 来查看自己的偏好，你可能会惊讶。  

## Explore mode VS Exploit mode  
In Exploit mode, you see works that the AI predicts you will like.  
In EXPLORE Mode, the AI shows you random documents.  
EXPLORE Mode is important to avoid modality collapse.   
在 EXPLORE Mode，AI 假装不知道你的偏好，随机展示作品。  
这很重要。如果没有 EXPLORE Mode，你会局限在单种风格里，恶性循环，与更多你喜欢的风格失之交臂。  

## Response
Negative: 我不想看到更多这类作品   
Ok: 一般般   
Has value: 有可取之处   
Good: 我若错过会觉得可惜   
Star: 存了   
You can hold alt + hotkey to select a button.   
按住 Alt 按首字母可以选择按钮。  

## Parameters 
Use notepad.exe to open `parameters.py`   
EXPLORE_PROB is the probability of entering EXPLORE Mode.  
VIEW_RATIO determines the top percentile that the AI will show you. For example, ".2" means in each batch of documents the AI will only show you the top 20% that are predicted to be good.   
ATTITUDE_TOWARDS_NOVEL_TAGS. If &gt;0, tags that are never shown before will be welcome. If =0, ai will use a balanced statictic model.  
JOB_POOL_SIZE is the size of the local pre-fetch cache. If the images load too slowly, try increasing this parameter. If Nozomi.la starts to refuse your connections, try lowering this parameter.   
调参   
使用记事本打开 `parameters.py`，更改参数。  
EXPLORE_PROB 是 EXPLORE Mode 的出现频率。  
VIEW_RATIO 决定推荐的精品程度。比如，".2"就会让AI只给你推荐每一批作品中预测你会最喜欢的20%。    
ATTITUDE_TOWARDS_NOVEL_TAGS. 如果 &gt;0, 从未见过的 tags 将会人为增加推荐概率；如果 =0，ai 会以以往tags的平均分数评估新tags。  
JOB_POOL_SIZE 是本地预抓取的池子大小。如果图片加载慢，尝试上调这一参数。如果Nozomi.la开始拒绝连接请求，说明我们并发请求太多了，试着下调这一参数。  

## Blacklist 
Add tag names to `blacklist.txt` to achieve force exclusion. They won't even show up in EXPLORE mode.   
The tag names must be the index names of the tags, not the display names. Run summarizeTags.py to see the index names.   
Warning: If a document is not well-tagged, it may not be excluded.   
在 `blacklist.txt` 中加入tag名，它们不会再出现，甚至 EXPLORE Mode 也不会。  
Tag名 必须是索引名，不能是显示名。运行 summarizeTags.py 来看索引名。  
然而，如果有一个作品它的 tag 不全，则可能成为漏网之鱼。  

## goods.py 
Run to download "good" documents.   
运行来下载 "Good" 作品。  

## Conclusion
如有建议，或者 bug反馈，请在 https://github.com/daniel-chin/nozomi.la-ai 进行 open issue。谢谢！
