from fabric.api import local

def test():
    local('python -mtests.test')
