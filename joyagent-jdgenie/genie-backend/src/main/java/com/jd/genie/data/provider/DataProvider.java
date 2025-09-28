package com.jd.genie.data.provider;


import com.jd.genie.data.QueryResult;


public interface DataProvider<T extends DataQueryRequest> {

    QueryResult queryData(T request) throws Exception;

    boolean queryForTest(T request);
}
