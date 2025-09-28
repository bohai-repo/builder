package com.jd.genie.config;

import com.jd.genie.config.data.DataAgentConfig;
import com.jd.genie.config.data.DataAgentConstants;
import com.jd.genie.config.data.EsConfig;
import com.jd.genie.config.data.QdrantConfig;
import com.jd.genie.service.ChatModelInfoService;
import com.jd.genie.service.ColumnValueSyncService;
import com.jd.genie.service.QdrantService;
import lombok.extern.slf4j.Slf4j;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.CommandLineRunner;
import org.springframework.stereotype.Component;

@Slf4j
@Component
public class DataAgentInitRunner implements CommandLineRunner {

    @Autowired
    private DataAgentConfig dataAgentConfig;
    @Autowired
    private QdrantService qdrantService;
    @Autowired
    private ChatModelInfoService chatModelInfoService;
    @Autowired
    private ColumnValueSyncService columnValueSyncService;


    @Override
    public void run(String... args) throws Exception {
        log.info("dataAgent config:{}", dataAgentConfig);
        QdrantConfig qdrantConfig = dataAgentConfig.getQdrantConfig();
        if (qdrantConfig.getEnable()) {
            qdrantService.createCosineCollection(DataAgentConstants.SCHEMA_COLLECTION_NAME, 1024);
            log.info("qdrant collection init success");
        }
        EsConfig esConfig = dataAgentConfig.getEsConfig();
        if (esConfig.getEnable()) {
            columnValueSyncService.initColumnValueIndex();
            log.info("column value es index init success");
        }
        chatModelInfoService.initModelInfo(dataAgentConfig);
    }
}
