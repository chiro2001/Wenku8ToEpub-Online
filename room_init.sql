-- 消息
CREATE TABLE message (
    -- 发送者，头像（展示变化用）
    uid INT,
    -- 消息id（排序用）
    mid INT,
    -- 重要：gid，表明所属以便SELECT
    gid INT,
    username VARCHAR(512),
    head VARCHAR(128),
    -- 类型：{'text', 'image', 'file'}
    type VARCHAR(32),
    -- 不一定是文本内容。如果是image或者file，将包含一个链接。
    text VARCHAR(8192)
);

-- 本群基本信息
CREATE TABLE info (
    -- Group id
    gid INT,
    -- Group name
    name VARCHAR(512),
    -- message id
    last_mid INT,
    -- 创建时间（GMT）varchar
    create_time VARCHAR(32),
    -- 目前成员个数
    member_number INT,
    -- 上次活跃时间
    last_post_time VARCHAR(32),
);

-- 成员-group关联列表（加群记录）
CREATE TABLE members (
    gid INT,
    username VARCHAR(256)
);

INSERT INTO info (gid, name, last_mid, create_time, member_number, last_post_time, flag) VALUES (0, "New group", 1, "", 0, "", "FLAG");
INSERT INTO message (uid, username, head, type, text) VALUES
    (0, "Administrator", "https://s.gravatar.com/avatar/544b5009873b27f5e0aa6dd8ffc1d3d8?s=512", "text", "欢迎加入本群组！");
