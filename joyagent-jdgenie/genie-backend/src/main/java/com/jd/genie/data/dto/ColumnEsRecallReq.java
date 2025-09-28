package com.jd.genie.data.dto;

import lombok.Data;

import java.util.List;
import java.util.Map;

@Data
public class ColumnEsRecallReq {
    private String query;
    private List<String> modelCodeList;
    private int limit = 100;
}
