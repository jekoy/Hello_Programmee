This is a repository for zhihu crawler.
written in Python 3.5

------ 知乎爬虫 ------

	API

登录知乎
login(user, password)

获取某个用户的知乎 id
get_hash_id(people)

get_followees_number(people)
获取某个用户关注者人数

获取某个用户的所有关注者
get_all_followees(people)

获取某个用户所有关注者的所有收藏夹
get_all_followees_collections(people)

获取某个用户的所有收藏夹
get_all_collections(people)

保存某个用户的所有收藏夹
store_all_collections(people)

更新收藏夹
update_collections(cookies)



V 0.1
爬取number字符串中的知乎收藏夹，每次爬取一页，将问题与答案写入collection文档，
按回车键爬取下一页。自动过滤图片

V 0.2
改进：
解决同一问题下有多个回答被连续收藏的问题
增加：
创建一个以收藏夹名字为名的文件夹，每次载入整个收藏夹，并将收藏夹的每一页创建一个以页码为名字的txt文档放入此文件夹

V 0.3
增加：
将people字符串改为某个知乎用户即可创建以用户名为文件夹名的文件夹，并爬取此用户所有的收藏夹。

V 0.4
增加：
登录知乎
改进：
解决因为没有登录知乎而无法保存部分用户收藏夹的问题

V 0.5
增加：
获取某个用户所有关注者的收藏夹（因为无法处理动态网页，只能获取前20个关注者）

V 0.6
增加：
更新自己所有的收藏夹（即更新自上次打开收藏夹之后更新的内容）

V 0.7
解决版本0.5中获取关注者时无法加载动态页面的问题

V 0.8
解决更新收藏夹时回答的格式问题并且将回答中的图片保存于当前目录
