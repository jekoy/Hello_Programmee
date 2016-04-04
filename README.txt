This is a repository for zhihu crawler.
written in Python 3.5

V 0.1
爬取number字符串中的知乎收藏夹，每次爬取一页，将问题与答案写入collection文档，
按回车键爬取下一页。自动过滤图片

V 0.2
改进：
	解决同一问题下有多个回答被连续收藏的问题
增加：
	创建一个以收藏夹名字为名的文件夹，每次载入整个收藏夹，并将收藏夹的每一页创建一个以页码为名字的txt文档放入此文件夹
