package com.jd.genie.data.provider.jdbc;

import com.jd.genie.data.SimpleTable;
import com.jd.genie.data.TableColumn;
import com.jd.genie.data.jdbc.catalog.AbstractJdbcCatalog;
import com.jd.genie.data.jdbc.connection.ConnectionWrapper;
import com.jd.genie.data.jdbc.connection.JdbcConnectionFactory;
import com.jd.genie.data.provider.DataMetaProvider;
import lombok.extern.slf4j.Slf4j;
import org.springframework.stereotype.Service;

import java.sql.*;
import java.util.ArrayList;
import java.util.List;

import static com.jd.genie.data.jdbc.catalog.AbstractJdbcCatalog.typeConvert;

@Slf4j
@Service
public class JdbcDataMetaProvider implements DataMetaProvider<JdbcQueryRequest> {

    @Override
    public List<SimpleTable> queryTables(JdbcQueryRequest request, String schemaPattern) throws SQLException {
        final ConnectionWrapper wrapper = JdbcConnectionFactory.getConnection(request.getJdbcConnectionConfig());
        try (Connection connection = wrapper.getConnection()) {
            return wrapper.getCatalog().listTables(connection, schemaPattern);
        }
    }

    @Override
    public List<TableColumn> queryColumns(JdbcQueryRequest request, String tableName, String schema) throws SQLException {
        final ConnectionWrapper wrapper = JdbcConnectionFactory.getConnection(request.getJdbcConnectionConfig());
        try (Connection connection = wrapper.getConnection()) {
            return wrapper.getCatalog().getTableColumns(connection, tableName, schema);
        }
    }

    @Override
    public List<TableColumn> getTableColumnsOfSql(JdbcQueryRequest request) throws SQLException {
        final ConnectionWrapper wrapper = JdbcConnectionFactory.getConnection(request.getJdbcConnectionConfig());
        request.setSql(wrapper.getJdbcDialect().formatSql(request.getSql()));
        log.info("jdbc meta 执行sql:{}", request.getSql());
        List<TableColumn> columnList = new ArrayList<>();
        try (Connection connection = wrapper.getConnection()) {
            try (
                    Statement ps = wrapper.createStatement(connection, request.getLimit());
                    ResultSet rs = ps.executeQuery(request.getSql())) {
                ResultSetMetaData metaData = rs.getMetaData();
                int columnCount = metaData.getColumnCount();

                for (int i = 1; i <= columnCount; i++) {
                    String name = metaData.getColumnLabel(i);
                    int intDataType = metaData.getColumnType(i);
                    JDBCType jdbcType = JDBCType.valueOf(intDataType);
                    String dataType = typeConvert(jdbcType);
                    TableColumn column = TableColumn.builder().name(name)
                            .comment(name)
                            .dataType(dataType)
                            .originDataType(jdbcType.name())
                            .position(i + 1)
                            .build();
                    columnList.add(column);
                }
            }

        }
        return columnList;
    }

}
