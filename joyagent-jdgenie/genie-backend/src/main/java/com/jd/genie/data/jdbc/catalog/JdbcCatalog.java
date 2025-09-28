
package com.jd.genie.data.jdbc.catalog;


import com.jd.genie.data.SimpleTable;
import com.jd.genie.data.TableColumn;
import com.jd.genie.data.exception.CatalogException;

import java.sql.Connection;
import java.util.List;

public interface JdbcCatalog {

    List<SimpleTable> listTables(Connection connection, String schema) throws CatalogException;

    List<TableColumn> getTableColumns(Connection connection, String tablePath, String schema) throws CatalogException;
}
