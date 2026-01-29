"""
Hierarchical Keyword Handler for Klar 4.0
Manages hierarchical keyword database with parent-child relationships
Supports multi-level keyword traversal and relevance scoring
"""

import json
from pathlib import Path
from typing import Dict, List, Set, Tuple, Optional
from collections import defaultdict
import sys
import os


def get_resource_path(relative_path):
    """Get absolute path to resource - works for dev and PyInstaller"""
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)


class HierarchicalKeywordHandler:
    """Handle hierarchical keyword database operations"""
    
    def __init__(self, db_file: str = "keywords_db_hierarchical.json"):
        self.db_file = db_file
        self.hierarchy = {}
        self.keyword_index = {}  # Maps keyword -> category IDs
        self.category_index = {}  # Maps category ID -> full category data
        self.parent_child_map = defaultdict(list)  # Maps parent -> children
        self.stopwords = set()
        self.metadata_config = {}
        self.domain_metadata = {}
        
        self.load_database()
    
    def load_database(self):
        """Load hierarchical keyword database"""
        db_path = get_resource_path(self.db_file)
        
        try:
            with open(db_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            self.hierarchy = data.get('hierarchy', {})
            self.stopwords = set(data.get('stopwords', []))
            self.metadata_config = data.get('metadata_search', {})
            self.domain_metadata = data.get('domain_metadata', {}).get('domains', {})
            
            # Build indexes
            self._build_indexes()
            
            print(f"[HierarchicalKeywords] Loaded {len(self.category_index)} categories")
            print(f"[HierarchicalKeywords] Indexed {len(self.keyword_index)} unique keywords")
            
        except FileNotFoundError:
            print(f"[HierarchicalKeywords] Warning: {db_path} not found")
            # Try fallback to old database
            self._load_fallback_database()
        except Exception as e:
            print(f"[HierarchicalKeywords] Error loading database: {e}")
            self._load_fallback_database()
    
    def _load_fallback_database(self):
        """Load old flat keyword database as fallback"""
        try:
            fallback_path = get_resource_path("keywords_db.json")
            with open(fallback_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # Convert flat to simple hierarchy
            mappings = data.get('mappings', {})
            for cat_id, cat_data in mappings.items():
                self.hierarchy[cat_id] = {
                    'id': cat_id,
                    'name': cat_data.get('category', cat_id),
                    'parent': None,
                    'level': 0,
                    'keywords': cat_data.get('keywords', []),
                    'priority_domains': cat_data.get('priority_domains', []),
                    'children': [],
                    'subcategories': {}
                }
            
            self.stopwords = set(data.get('stopwords', []))
            self._build_indexes()
            
            print(f"[HierarchicalKeywords] Loaded {len(self.category_index)} categories from fallback")
            
        except Exception as e:
            print(f"[HierarchicalKeywords] Error loading fallback: {e}")
    
    def _build_indexes(self):
        """Build keyword and category indexes"""
        self.keyword_index = defaultdict(set)
        self.category_index = {}
        self.parent_child_map = defaultdict(list)
        
        for cat_id, category in self.hierarchy.items():
            # Index category
            self.category_index[cat_id] = category
            
            # Index parent-child relationships
            parent = category.get('parent')
            if parent:
                self.parent_child_map[parent].append(cat_id)
            
            # Index keywords for this category
            keywords = category.get('keywords', [])
            for keyword in keywords:
                keyword_lower = keyword.lower().strip()
                if keyword_lower and keyword_lower not in self.stopwords:
                    self.keyword_index[keyword_lower].add(cat_id)
            
            # Index subcategories
            subcategories = category.get('subcategories', {})
            for sub_id, sub_cat in subcategories.items():
                # Index subcategory
                self.category_index[sub_id] = sub_cat
                
                # Index parent-child
                self.parent_child_map[cat_id].append(sub_id)
                
                # Index keywords for subcategory
                sub_keywords = sub_cat.get('keywords', [])
                for keyword in sub_keywords:
                    keyword_lower = keyword.lower().strip()
                    if keyword_lower and keyword_lower not in self.stopwords:
                        self.keyword_index[keyword_lower].add(sub_id)
    
    def find_categories(self, query: str) -> List[Dict]:
        """
        Find categories matching query keywords
        
        Args:
            query: Search query
            
        Returns:
            List of matching categories with scores
        """
        query_lower = query.lower()
        query_words = [w.strip() for w in query_lower.split() if w.strip() not in self.stopwords]
        
        if not query_words:
            return []
        
        # Find categories for each keyword
        category_scores = defaultdict(float)
        
        for word in query_words:
            # Exact match
            if word in self.keyword_index:
                for cat_id in self.keyword_index[word]:
                    category_scores[cat_id] += 1.0
            
            # Partial match (contains)
            for keyword, cat_ids in self.keyword_index.items():
                if word in keyword or keyword in word:
                    for cat_id in cat_ids:
                        category_scores[cat_id] += 0.5
        
        # Sort by score
        sorted_categories = sorted(
            category_scores.items(),
            key=lambda x: x[1],
            reverse=True
        )
        
        # Build result
        results = []
        for cat_id, score in sorted_categories[:10]:  # Top 10
            category = self.category_index.get(cat_id)
            if category:
                results.append({
                    'id': cat_id,
                    'name': category.get('name', cat_id),
                    'level': category.get('level', 0),
                    'parent': category.get('parent'),
                    'score': score,
                    'priority_domains': category.get('priority_domains', []),
                    'metadata_tags': category.get('metadata_tags', [])
                })
        
        return results
    
    def get_category_hierarchy(self, category_id: str) -> List[str]:
        """
        Get full hierarchy path for a category (from root to category)
        
        Args:
            category_id: Category ID
            
        Returns:
            List of category IDs from root to target
        """
        path = []
        current_id = category_id
        
        while current_id:
            path.insert(0, current_id)
            category = self.category_index.get(current_id)
            if not category:
                break
            current_id = category.get('parent')
        
        return path
    
    def get_related_categories(self, category_id: str) -> Dict[str, List[str]]:
        """
        Get related categories (parent, children, siblings)
        
        Args:
            category_id: Category ID
            
        Returns:
            Dictionary with parent, children, and siblings
        """
        category = self.category_index.get(category_id)
        if not category:
            return {'parent': None, 'children': [], 'siblings': []}
        
        parent_id = category.get('parent')
        children_ids = self.parent_child_map.get(category_id, [])
        
        # Get siblings (other children of same parent)
        siblings = []
        if parent_id:
            siblings = [
                c for c in self.parent_child_map.get(parent_id, [])
                if c != category_id
            ]
        
        return {
            'parent': parent_id,
            'children': children_ids,
            'siblings': siblings
        }
    
    def get_all_keywords_for_category(self, category_id: str, include_children: bool = True) -> List[str]:
        """
        Get all keywords for a category and optionally its children
        
        Args:
            category_id: Category ID
            include_children: Include child category keywords
            
        Returns:
            List of all keywords
        """
        keywords = set()
        
        # Get category keywords
        category = self.category_index.get(category_id)
        if category:
            keywords.update(category.get('keywords', []))
            
            # Get children keywords
            if include_children:
                children = self.parent_child_map.get(category_id, [])
                for child_id in children:
                    child_cat = self.category_index.get(child_id)
                    if child_cat:
                        keywords.update(child_cat.get('keywords', []))
        
        return list(keywords)
    
    def get_domains_for_category(self, category_id: str, include_parents: bool = True) -> List[str]:
        """
        Get priority domains for a category
        
        Args:
            category_id: Category ID
            include_parents: Include parent category domains
            
        Returns:
            List of priority domains
        """
        domains = set()
        
        # Get category domains
        category = self.category_index.get(category_id)
        if category:
            domains.update(category.get('priority_domains', []))
        
        # Get parent domains
        if include_parents:
            hierarchy = self.get_category_hierarchy(category_id)
            for cat_id in hierarchy:
                cat = self.category_index.get(cat_id)
                if cat:
                    domains.update(cat.get('priority_domains', []))
        
        return list(domains)
    
    def get_metadata_tags_for_category(self, category_id: str) -> List[str]:
        """Get metadata tags for a category"""
        category = self.category_index.get(category_id)
        if category:
            return category.get('metadata_tags', [])
        return []
    
    def get_domain_metadata(self, domain: str) -> Optional[Dict]:
        """Get metadata for a specific domain"""
        return self.domain_metadata.get(domain)
    
    def search_by_metadata_tags(self, tags: List[str]) -> List[Dict]:
        """
        Search categories by metadata tags
        
        Args:
            tags: List of metadata tags to search for
            
        Returns:
            List of matching categories
        """
        if not tags:
            return []
        
        tag_set = set(t.lower() for t in tags)
        matches = []
        
        for cat_id, category in self.category_index.items():
            cat_tags = set(t.lower() for t in category.get('metadata_tags', []))
            
            # Calculate overlap
            overlap = len(tag_set & cat_tags)
            if overlap > 0:
                score = overlap / len(tag_set)
                matches.append({
                    'id': cat_id,
                    'name': category.get('name', cat_id),
                    'score': score,
                    'matching_tags': list(tag_set & cat_tags),
                    'priority_domains': category.get('priority_domains', [])
                })
        
        # Sort by score
        matches.sort(key=lambda x: x['score'], reverse=True)
        return matches[:10]
    
    def get_category_tree(self, category_id: str = None, max_depth: int = 2) -> Dict:
        """
        Get category tree structure
        
        Args:
            category_id: Root category (None = all top-level)
            max_depth: Maximum depth to traverse
            
        Returns:
            Tree structure
        """
        if category_id:
            category = self.category_index.get(category_id)
            if not category:
                return {}
            
            tree = {
                'id': category_id,
                'name': category.get('name', category_id),
                'level': category.get('level', 0),
                'children': []
            }
            
            if max_depth > 0:
                children = self.parent_child_map.get(category_id, [])
                for child_id in children:
                    child_tree = self.get_category_tree(child_id, max_depth - 1)
                    if child_tree:
                        tree['children'].append(child_tree)
            
            return tree
        else:
            # Get all top-level categories
            top_level = []
            for cat_id, category in self.category_index.items():
                if category.get('level', 0) == 0 and not category.get('parent'):
                    tree = self.get_category_tree(cat_id, max_depth)
                    if tree:
                        top_level.append(tree)
            
            return {'root': True, 'children': top_level}
    
    def get_statistics(self) -> Dict:
        """Get database statistics"""
        total_categories = len(self.category_index)
        total_keywords = len(self.keyword_index)
        
        # Count by level
        levels = defaultdict(int)
        for category in self.category_index.values():
            level = category.get('level', 0)
            levels[level] += 1
        
        return {
            'total_categories': total_categories,
            'total_keywords': total_keywords,
            'categories_by_level': dict(levels),
            'stopwords': len(self.stopwords),
            'metadata_enabled': self.metadata_config.get('enabled', False)
        }
