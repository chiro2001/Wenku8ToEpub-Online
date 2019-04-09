CREATE TABLE users (
    -- 用户id号。
    uid INT,
    -- 最重要的用户名以及密码。密码按照MD5储存。
    -- 校验密码只校验MD5。
    username VARCHAR(64),
    password VARCHAR(128),
    -- 昵称
    name VARCHAR(512),
    email VARCHAR(512),
    -- 头像
    head VARCHAR(512),
    -- 用户状态：在线(Online(1))或者下线(Offline(0))
    status INT
);

---- 用户与加入的房间号码
--CREATE TABLE rooms (
--    username VARCHAR(512),
--    gid INT
--);

-- 维护用表
CREATE TABLE maintain (
    -- 最新一个用户id和群组id，消息id。
    last_uid INT,
    last_gid INT,
    -- 用于识别该列
    flag VARCHAR(32)
);

-- 鉴权认证储存
CREATE TABLE auth (
    username VARCHAR(512),
    auth VARCHAR(128)
);

-- 初始化维护
INSERT INTO maintain (last_uid, last_gid, flag) VALUES (0, 0, "FLAG");
