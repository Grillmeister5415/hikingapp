from rest_framework.pagination import PageNumberPagination

class StandardResultsSetPagination(PageNumberPagination):
    """
    Standard-Paginierungsklasse, die es dem Client erlaubt, die Seitengrösse
    über die Query-Parameter 'page' und 'page_size' zu steuern.
    """
    page_size = 10  # Standard-Seitengrösse
    page_size_query_param = 'page_size'  # Der URL-Parameter, z.B. /api/trips/?page_size=25
    max_page_size = 1000 # Maximale Seitengrösse zum Schutz der Performance

    def get_page_size(self, request):
        """
        Überschreibt die Standard-Methode, um 'None' als page_size zu erlauben,
        was die Paginierung für den "Alle anzeigen"-Fall deaktiviert.
        """
        if self.page_size_query_param:
            page_size = request.query_params.get(self.page_size_query_param)
            if page_size and page_size.lower() == 'none':
                return None # Deaktiviert die Paginierung
            try:
                return super().get_page_size(request)
            except (KeyError, ValueError):
                pass

        return self.page_size