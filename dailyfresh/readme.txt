项目使用的django为1.8.2，项目整体分为四个模块，用户模块、商品模块、购物车模块以及订单模块
用户模块实现了用户的注册、登陆、退出、个人中心以及发送激活邮件激活账号功能（celery异步任务队列）
商品模块实现了首页、商品详情页、商品列表页以及商品搜索功能（haystack全文检索框架+whoosh搜索引擎+jieba分词模块）
购物车模块实现了商品的增加、删除、修改、查询
订单模块实现了确认订单、提交订单、请求支付（支付宝支付）、查询支付结果、评论
为了优化项目采用了fastdfs并结合nginx提高网站访问图片的效率，为首页页面设置缓存，并提供静态化，利用nginx调度外部访问实现负载均衡
为了预防高并发采用了数据库的事务特性（需要更改mysql的隔离级别为Read Committed），乐观锁概念（查询时不锁数据，提交更改时进行判断）
最后项目部署时，因为是在同一台ubuntu虚拟机上，舍弃了页面静态化
