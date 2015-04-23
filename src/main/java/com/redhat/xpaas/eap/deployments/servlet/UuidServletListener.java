package com.redhat.xpaas.eap.deployments.servlet;

import java.util.UUID;

import javax.servlet.ServletContextEvent;
import javax.servlet.ServletContextListener;
import javax.servlet.annotation.WebListener;

@WebListener
public class UuidServletListener implements ServletContextListener {

    @Override
    public void contextDestroyed(ServletContextEvent event) {
        
    }

    @Override
    public void contextInitialized(ServletContextEvent event) {
        event.getServletContext().setAttribute("servletId", UUID.randomUUID().toString());
    }

}
