from fabric.api import local

def test():
    local('cd fahrplan && python -mtests.test')
