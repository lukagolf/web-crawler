#!/usr/bin/env python3

import argparse
import socket
import ssl
import re

DEFAULT_SERVER = "project5.3700.network"
DEFAULT_PORT = 443

USERAGENT = 'PostmanRuntime/7.29.0'
LOGIN_PATH = "/accounts/login/?next=/fakebook/"
HOME_PAGE = "/fakebook/"

class Crawler:

    """
    A class that represents the web crawler.

    Attributes
    ----------
    server : str
        address of the site that we will crawl
    port : int
        the port number we will connect to
    username : str
        the username the crawler will use to login with
    password : str
        the password the crawler will use to login with
    useragent : str
        the useragent string our crawler when use in HTTP requests
    csrftoken : str
        the csrftoken given by the website for us to use in our HTTP requests
    sessionid : str
        the ID for our current session with the website
    flags : list
        contains the flags that the crawler has found
    frontier : list
        the page IDs we have not traversed yet
    pages_visited : list
        the page IDs we have already gone through
    mysocket : socket
        the socket we will use for our communication with the website
    """

    def __init__(self, args):
        """
        Parameters
        ----------
        args.server : str
            the url of the server we'll connect to
        args.port : int
            the port number we will connect to
        args.username : str
            the username we will use to login with
        args.password : str
            the password we will use to login with
        """
        self.server = args.server
        self.port = args.port
        self.username = args.username
        self.password = args.password
        self.useragent = USERAGENT
        self.csrftoken = ''
        self.sessionid = ''
        self.flags = []
        self.frontier = []
        self.pages_visited = []
        self.mysocket = None

    def init_socket(self):
        """
        Initializes the socket that we will use to communicate with the website.
        """
        if self.mysocket is not None:
            self.mysocket.close()
        mysocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        mysocket.connect((self.server, self.port))
        self.mysocket = ssl.create_default_context().wrap_socket(mysocket, server_hostname=self.server)

    def check_for_flags(self, data):
        """
        Looks for flags in the given page data and add them to self.flags if found.
        """
        curr_flags_tag = re.findall(r'<h3 class=.secret_flag[^>]*>FLAG: (.{64})</h3>', data)
        if len(curr_flags_tag) > 0:
            self.flags.extend(curr_flags_tag)
            
    def print_flags(self):
        """
        Prints our the flags that were found.
        """
        if len(self.flags)!=5:
            print("ERROR")
        for flag in self.flags:
            print(flag)

    def create_get_request_str(self, path):
        """
        Forms a GET request aimed at the given path on the website.
        """
        request = "GET %s HTTP/1.1\r\n" % path
        request += 'HOST: %s\r\n' % self.server
        request += "User-Agent: %s\r\n" % self.useragent
        request += 'Accept: */*\r\n'
        request += 'Referer: https://project5.3700.network/\r\n'
        if self.csrftoken != '' and self.sessionid != '':
            request += 'Cookie: csrftoken=%s; sessionid=%s\r\n' % (
                self.csrftoken, self.sessionid)
        elif self.csrftoken != '' and self.sessionid == '':
            request += 'Cookie: csrftoken=%s\r\n' % self.csrftoken
        
        request += 'Connection: keep-alive\r\n'
        request += "\r\n"
        return request

    def create_login_request_str(self, token):
        """
        Creates the HTTP request when we are logging into the website.
        """
        body = 'username=%s&password=%s&csrfmiddlewaretoken=%s' % (self.username, self.password, token)

        request = "POST %s HTTP/1.1\r\n" % LOGIN_PATH
        request += 'HOST: %s\r\n' % self.server
        request += "User-Agent: %s\r\n" % self.useragent
        request += 'Accept: */*\r\n'
        request += 'Referer: https://project5.3700.network/\r\n'
        request += 'Connection: keep-alive\r\n'
        request += 'Cookie: csrftoken=%s\r\n' % self.csrftoken
        request += 'Content-Type: application/x-www-form-urlencoded\r\n'
        request += 'Content-Length: %d\r\n' % len(body.encode())
        request += "\r\n"
        request += body 
        return request

    def update_cookie(self, header):
        """
        Update our cookies when we detect the csrftoken and sessionid values from the response from the website.
        """
        cookies = re.findall(r'Set-Cookie:(.*)\r\n', header)
        for cookie in cookies:
            csrftokens = re.findall(r'csrftoken=([^;]*)', cookie)
            if len(csrftokens)>0:
                self.csrftoken = csrftokens[0]
            sessionids = re.findall(r'sessionid=([^;]*)', cookie)
            if len(sessionids)>0:
                self.sessionid = sessionids[0]
        
    def send_get_request(self, path):
        """ Crafts and sends a GET request with the given prompt. Returns the response from the server """
        request = self.create_get_request_str(path)
        self.mysocket.send(request.encode("ascii"))

    def login(self):
        """
        Perfoms the login process and updates the appropriate cookie values.
        """
        header, data = self.send_get_and_receive_response(LOGIN_PATH)
        self.update_cookie(header)

        # Search for the csrfmiddlewaretoken using regex
        result = re.findall(r'<input type="hidden" name="csrfmiddlewaretoken" value="(.*)">', data)
        token = result[0]

        # Create a login request with the csrfmiddlewaretoken we found
        request = self.create_login_request_str(token)
        
        # Init the socket, send the login request, and save the csrf token and session ID
        self.init_socket()
        self.mysocket.send(request.encode("ascii"))
        data = self.mysocket.recv(16384).decode('ascii')
        self.update_cookie(data)

    def send_get_and_receive_response(self, request):
        """
        Sends a GET message with the request and returns the response from the website.
        """
        while True:
            response = ''
            complete = False
            while not complete:
                try:
                    self.send_get_request(request)
                    response = self.mysocket.recv(16384).decode('ascii')
                    if len(response) > 0:
                        complete = True
                except:
                    # If the connection has closed, restart the socket
                    self.init_socket()
                    complete = False
                
            pair = response.split('\r\n\r\n', 1)
            header = pair[0]
            code = re.findall(r'^HTTP/1.1 ([^ ]+)', header)[0]

            # Here, we handle HTTP codeeds from the server's response
            if code == "302":
                locations = re.findall(r'\r\nLocation: ([^\r]+)\r\n', header)
                if locations > 0:
                    self.frontier(locations[0])
                return header, ""
            elif code == "403":
                return header, ""
            elif code == "200":
                if len(pair)==1:
                    return header, ""
                self.check_for_flags(pair[1])
                return header, pair[1]

    def crawl_page(self, path):
        """
        Goes through the links on the Fakebook page and extracts the links.
        The links are added to the frontier for searching.
        """
        header, data = self.send_get_and_receive_response(path)
        
        crawl_paths = re.findall(r'href="(/fakebook[^"]+)"', data)
        if len(crawl_paths) > 0:
            self.frontier.extend(crawl_paths)
    
    def crawl(self):
        """
        Crawls through the entirety of Fakebook.
        """
        self.frontier.append(HOME_PAGE)

        while len(self.flags) < 5 and len(self.frontier) > 0:
            curr_page = self.frontier.pop(0)
            if curr_page in self.pages_visited:
                continue
            self.pages_visited.append(curr_page)
            self.crawl_page(curr_page)


    def run(self):
        """
        Sets up everything, crawls Fakebook, and prints the flags when its done searching.
        """
        self.init_socket()
        self.login()
        self.crawl()
        self.print_flags()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='crawl Fakebook')
    parser.add_argument('-s', dest="server", type=str, default=DEFAULT_SERVER, help="The server to crawl")
    parser.add_argument('-p', dest="port", type=int, default=DEFAULT_PORT, help="The port to use")
    parser.add_argument('username', type=str, help="The username to use")
    parser.add_argument('password', type=str, help="The password to use")
    args = parser.parse_args()
    sender = Crawler(args)
    sender.run()
