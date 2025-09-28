package com.jd.genie.config.data;

import com.jd.genie.util.ESUtil;
import lombok.extern.slf4j.Slf4j;
import org.elasticsearch.client.RestHighLevelClient;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;

@Slf4j
@Configuration
public class Es7HighLevelClientConfig {

    @Autowired
    DataAgentConfig dataAgentConfig;

    @Bean(name = "dataAgentEsClient")
    public RestHighLevelClient dataAgentEsClient() {
        EsConfig esConfig = dataAgentConfig.getEsConfig();
        return ESUtil.buildRestClient(esConfig.getHost(), esConfig.getUser(), esConfig.getPassword(), 30000);
    }


}
