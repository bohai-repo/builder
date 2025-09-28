package com.jd.genie;

import org.mybatis.spring.annotation.MapperScan;
import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;

@MapperScan("com.jd.genie.mapper")
@SpringBootApplication
public class GenieApplication {
    public static void main(String[] args) {
        SpringApplication.run(GenieApplication.class, args);
    }
}