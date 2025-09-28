package com.jd.genie.util;

import com.jd.genie.config.data.DbConfig;
import com.jd.genie.data.jdbc.JdbcConnectionConfig;
import com.jd.genie.data.jdbc.dialect.DialectEnum;

public class JdbcUtils {

    public static JdbcConnectionConfig parseJdbcConnectionConfig(DbConfig dbConfig) {
        JdbcConnectionConfig jdbcConnectionConfig = new JdbcConnectionConfig();
        jdbcConnectionConfig.setUrl(createJdbcUrl(dbConfig.getType(), dbConfig.getHost(), dbConfig.getPort(), dbConfig.getSchema()));
        jdbcConnectionConfig.setKey(dbConfig.getKey());
        jdbcConnectionConfig.setUserName(dbConfig.getUsername());
        jdbcConnectionConfig.setPassword(dbConfig.getPassword());
        jdbcConnectionConfig.setDataSourceType(dbConfig.getType());
        return jdbcConnectionConfig;
    }

    public static String createJdbcUrl(String type, String host, int port, String schemaName) {
        DialectEnum dialectEnum = DialectEnum.of(type);
        String base = dialectEnum.getUrlPrefix() + host;
        if (port > 0) {
            return base + ":" + port + dialectEnum.getSuffixDelimiter() + schemaName + dialectEnum.getUrlEndWith();
        }
        return dialectEnum.getUrlPrefix() + host + dialectEnum.getSuffixDelimiter() + schemaName + dialectEnum.getUrlEndWith();
    }

}
