from django.utils.deprecation import MiddlewareMixin
from django.shortcuts import render, redirect


class AuthMiddleWare(MiddlewareMixin):
    '''
    自定义的中间件，django的中间件是一个类。需要继承 MiddlewareMixin
    '''

    def process_request(self, request):
        '''
        请求时经过的中间件
        :param request:
        :return:
        '''
        if request.path_info == '/login/':
            # 如果return为空（None）就继续往后走
            return
        if request.path_info == '/signup/':
            # 如果return为空（None）就继续往后走
            return
        # 获取当前访问用户的登录信息，如果能获取到，就往后走
        info_dict = request.session.get('userinfo')
        if info_dict:
            return
        return redirect('/login/')
