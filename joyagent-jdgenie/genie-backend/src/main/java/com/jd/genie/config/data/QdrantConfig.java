package com.jd.genie.config.data;

import lombok.Data;

@Data
public class QdrantConfig {
    private Boolean enable;
    private String host;
    private int port;
    private String apiKey;
    private String embeddingUrl;
}
