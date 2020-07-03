import urllib.request as urlrq
import ssl
import json
import os
import sys
import time
from datetime import datetime
from html_table_parser import HTMLTableParser
from emailer import ConnectionAlerts

LOG_ON = True


class TableScraper:
    def __init__(self, url_site, table_num,start_row,name_col,value_col, id_col):
        self.url = url_site
        self.table_num = table_num
        self.start_row=start_row
        self.name_col = name_col
        self.val_col = value_col
        self.id_col = id_col
 
    def scrape(self):
        items=[]
        count = 0
        response = self._make_http_request()
        tables = self._get_tables(response)
        if self.table_num < len(tables):
            if self.start_row < len(tables[self.table_num]):
                for row in tables[self.table_num]:
                    if count > self.start_row:
                        if self.name_col < len(row) and  self.val_col < len(row) and self.id_col < len(row):
                            if row[self.name_col] != "" and row[self.val_col] != "" and row[self.id_col] != "":
                                element = {"name": row[self.name_col], "value": row[self.val_col], "id": row[self.id_col]} 
                                items.append(element) 
                    count = count + 1 
        return items

    def _get_tables(self, data):
        p = HTMLTableParser()
        p.feed(data)

        return p.tables        
    def _make_http_request(self):
        url_resource = urlrq.urlopen(self.url)
        response = url_resource.read()
        return response.decode("utf-8")

class BTRouterState:
    
    def __init__(self, config):
        self.config = config

    def _log(self, msg):
        if LOG_ON:
            log = open(self.config.log_file, 'a+')
            log.write(msg)
            log.close()

    def save(self):
        self._log("Scraping BT Router: %s \n" % str(self._get_time()))
        current = self._get_current_state()
        last = self._get_last_state()
        if 'data' not in last:
            last = {'data':[]}
        if not self._states_equal(current['data'],last['data']):
            self._remove_last_state()
            self._save_current_state(current)
            self._add_current_state_to_history(current)
            if self.config.are_alerts_configured():
                alerter = ConnectionAlerts(self.config,
                                           last['data'], current['data'])
                alerter.send_all_alerts()
                
    def _get_current_state(self):
        scraper = TableScraper(self.config.router,9,1,1,3,2)
        table = scraper.scrape()
        return {'data': table}

    def _get_last_state(self):
        data = {}
        try:
            json_file = open(self.config.state_file)
            json_data = json_file.read()
            data = json.loads(json_data)
            json_file.close()
        except Exception:
            self._log("Failed to read file '%s'" % self.config.state_file)
        return data

    def _remove_last_state(self):
        os.remove(self.config.state_file)

    def _save_current_state(self,current):
        state_file =  open(self.config.state_file,'w+')
        json.dump(current, state_file)
        state_file.close()

    def _add_current_state_to_history(self,current):
        current['time'] = self._get_time()
        history_file =  open(self.config.history_file, 'a+')
        json.dump(current, history_file)
        history_file.write('\n')
        history_file.close()

    def _get_time(self):
        current = {}
        epoch  = int(time.time())
        utc_str = datetime.utcnow().strftime("%d-%m-%Y %H:%M:%S")
        current = {'epoch': epoch, 'utc': utc_str}
        return current

    def _states_equal(self, list1, list2):
        #Python arrays are only equal if element positions are same
        #Since we do not care about positions of elements in array
        #we have to do a little more work to compare states
        if len(list1) != len(list2):
            return False
        for item1 in list1:
           if item1 not in list2:
               return False
        return True

class BTRouterConfig():
    def __init__(self, path=None):
        # Examples of config settings
        self.frequency = 300 # 300 seconds
        self.router = "http://192.168.1.254"
        self.state_file = "/var/bt_router_scraper/state/current"
        self.history_file = "/var/bt_router_scraper/state/history"
        self.log_file = "/var/log/bt_router_scraper/all.log"
        self.alerts_conf = "/var/bt_router_scraper/conf/email_alerts.json",
        self.friendly_names = "/var/bt_router_scraper/conf/friendly_names.json"
        # Non required
        self.alerts_username = None
        self.alerts_password = None
        self.alerts_smtp_address = None
        self.alerts_smtp_port = None

        if path:
            try:
                json_file = open(path)
                json_data = json_file.read()
                conf = json.loads(json_data)
                json_file.close()
                if conf.get("frequency"):
                    self.frequency = conf.get("frequency")
                else:
                    print("Failed to set required parameter: frequency")
                    sys.exit(-1)
                if conf.get("router"):
                    self.router = conf.get("router")
                else:
                    print("Failed to set required parameter: router")
                    sys.exit(-1)
                if conf.get("state_file"):
                    self.state_file = conf.get("state_file")
                else:
                    print("Failed to set required parameter: state_file")
                    sys.exit(-1)
                if conf.get("history_file"):
                    self.history_file = conf.get("history_file")
                else:
                    print("Failed to set required parameter: history_file")
                    sys.exit(-1)
                if conf.get("log_file"):
                    self.log_file = conf.get("log_file")
                else:
                    print("Failed to set required parameter: log_file")
                    sys.exit(-1)
                if conf.get("alerts_conf"):
                    self.alerts_conf = conf.get("alerts_conf")
                else:
                    print("Failed to set required parameter: alerts_conf_")
                    sys.exit(-1)
                if conf.get("friendly_names"):
                    self.friendly_names = conf.get("friendly_names")
                else:
                    print("Failed to set required parameter: friendly_names")
                    sys.exit(-1)
                # Non required
                if conf.get("alerts_username"):
                    self.alerts_username = conf.get("alerts_username")
                if conf.get("alerts_password"):
                    self.alerts_password = conf.get("alerts_password")
                if conf.get("alerts_smtp_address"):
                    self.alerts_smtp_address = conf.get("alerts_smtp_address")
                if conf.get("alerts_smtp_port"):
                    self.alerts_smtp_port = conf.get("alerts_smtp_port")


            except Exception as ex:
                print("Failed to load config file '%s': '%s'" %(path, str(ex)))
                sys.exit(-1)

    def are_alerts_configured(self):
        configured = self.alerts_username and \
                         self.alerts_password and \
                         self.alerts_smtp_address and \
                         self.alerts_smtp_port  and \
                         self.alerts_conf
        return configured    

def main():
    # Main code here:
    config = BTRouterConfig("/etc/bt_router_scraper/conf.json")
    router_state = BTRouterState(config)
    while True:
        router_state.save()
        time.sleep(config.frequency)
    
if __name__ == "__main__":
    main()
