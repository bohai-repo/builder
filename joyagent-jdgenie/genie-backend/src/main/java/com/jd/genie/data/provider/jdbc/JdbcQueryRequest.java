package com.jd.genie.data.provider.jdbc;

import com.jd.genie.data.jdbc.JdbcConnectionConfig;
import com.jd.genie.data.provider.DataQueryRequest;
import lombok.Data;

@Data
public class JdbcQueryRequest implements DataQueryRequest {

    private JdbcConnectionConfig jdbcConnectionConfig;
    private String sql;
    private int limit;

    private int pageIndex;
    private int pageSize;
}
