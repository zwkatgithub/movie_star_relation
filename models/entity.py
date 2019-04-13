class Entity:


    def __init__(self):
        if not hasattr(self.__class__, 'table_name'):
            self.table_name = self.__class__.__name__.lower()
        else:
            self.table_name = self.__class__.table_name
    
    @property
    def sql(self):
        attrs, values = self._get_value()
        return "INSERT INTO {table_name} ({attrs})  VALUES ({values});".format(
            table_name = self.table_name,
            attrs = attrs,
            values = values
        )

    def _get_value(self):
        values = []
        attrs = []
        for attr_, value in self.__dict__.items():
            if attr_ == 'table_name':
                continue
            attrs.append(attr_)
            if isinstance(value, str):
                values.append('\'{}\''.format(value.replace('\'','\\\'')))
            elif value is None:
                values.append("null")
            else:
                values.append('{}'.format(value))
        return ','.join(attrs) , ','.join(values)

