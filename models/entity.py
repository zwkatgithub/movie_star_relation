class Entity:


    def __init__(self):
        if not hasattr(self.__class__, 'table_name'):
            self.table_name = self.__class__.__name__.lower()
        else:
            self.table_name = self.__class__.table_name
    
    @property
    def sql(self):
        return "INSERT IN TO {table_name} VALUE ({value});".format(
            table_name = self.table_name,
            value = self._get_value()
        )

    def _get_value(self):
        values = []
        for attr_, value in self.__dict__.items():
            if isinstance(value, str):
                values.append('{}=\'{}\''.format(attr_, value))
            elif value is None:
                values.append("{}=null".format(attr_))
            else:
                values.append('{}={}'.format(attr_, value))
        return ','.join(values)

