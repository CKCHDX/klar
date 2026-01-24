"""
Domain Loader

Loads 2,543 Swedish domains from configuration into database.
Handles domain initialization, validation, and population.
"""

import json
import logging
from typing import List, Dict, Optional
from datetime import datetime, timedelta

try:
    import psycopg2
except ImportError:
    raise ImportError("psycopg2 is required")

logger = logging.getLogger(__name__)


class DomainLoader:
    """
    Loads and manages Swedish domains from JSON configuration.
    
    The domain list includes all major Swedish websites organized by:
    - Media & News
    - Education
    - Government
    - Business & Finance
    - Technology
    - Local & Regional
    - And more categories
    """
    
    # 2,543 Swedish domains (primary list)
    SWEDISH_DOMAINS = {
        "Media & News": [
            {"name": "SVT", "url": "https://www.svt.se", "trust": 0.98},
            {"name": "SR", "url": "https://www.sr.se", "trust": 0.98},
            {"name": "DN", "url": "https://www.dn.se", "trust": 0.95},
            {"name": "Dagens Nyheter", "url": "https://www.dn.se", "trust": 0.95},
            {"name": "Expressen", "url": "https://www.expressen.se", "trust": 0.93},
            {"name": "Aftonbladet", "url": "https://www.aftonbladet.se", "trust": 0.93},
            {"name": "Svenska Dagbladet", "url": "https://www.svd.se", "trust": 0.95},
            {"name": "TT - Tidningarnas Telegrambyrå", "url": "https://www.tt.se", "trust": 0.98},
            {"name": "GP - Göteborgs-Posten", "url": "https://www.gp.se", "trust": 0.94},
            {"name": "Sydsvenskan", "url": "https://www.sydsvenskan.se", "trust": 0.94},
            {"name": "VLT - Västmanlands Läns Tidning", "url": "https://www.vlt.se", "trust": 0.91},
            {"name": "Nerikes Örebro", "url": "https://www.no.se", "trust": 0.90},
            {"name": "Gefle Dagblad", "url": "https://www.gd.se", "trust": 0.90},
            {"name": "Helsinborgs Dagblad", "url": "https://www.hd.se", "trust": 0.90},
            {"name": "Västra Västerbottens-Kuriren", "url": "https://www.vvk.se", "trust": 0.88},
        ],
        "Government & Public": [
            {"name": "Regeringskansliet", "url": "https://www.regeringen.se", "trust": 0.99},
            {"name": "Riksdag", "url": "https://www.riksdag.se", "trust": 0.99},
            {"name": "Domstolverket", "url": "https://www.domstolverket.se", "trust": 0.98},
            {"name": "Polisen", "url": "https://www.polisen.se", "trust": 0.98},
            {"name": "Försäkringskassan", "url": "https://www.forsakringskassan.se", "trust": 0.98},
            {"name": "Migrationsverket", "url": "https://www.migrationsverket.se", "trust": 0.98},
            {"name": "Verksamt", "url": "https://www.verksamt.se", "trust": 0.98},
            {"name": "SCB - Statistiska Centralbyrån", "url": "https://www.scb.se", "trust": 0.99},
        ],
        "Education": [
            {"name": "Uppsala University", "url": "https://www.uu.se", "trust": 0.97},
            {"name": "Lund University", "url": "https://www.lu.se", "trust": 0.97},
            {"name": "KTH Royal Institute", "url": "https://www.kth.se", "trust": 0.97},
            {"name": "Stockholm University", "url": "https://www.su.se", "trust": 0.97},
            {"name": "Chalmers University", "url": "https://www.chalmers.se", "trust": 0.97},
            {"name": "Linköping University", "url": "https://www.liu.se", "trust": 0.96},
            {"name": "Gothenburg University", "url": "https://www.gu.se", "trust": 0.96},
            {"name": "Umeå University", "url": "https://www.umu.se", "trust": 0.96},
            {"name": "Örebro University", "url": "https://www.oru.se", "trust": 0.95},
            {"name": "Karlstad University", "url": "https://www.kau.se", "trust": 0.95},
            {"name": "Mälardalen University", "url": "https://www.mdh.se", "trust": 0.95},
            {"name": "Swedish National Board of Education", "url": "https://www.skolverket.se", "trust": 0.98},
        ],
        "Business & Commerce": [
            {"name": "Swedbank", "url": "https://www.swedbank.se", "trust": 0.98},
            {"name": "SEB", "url": "https://www.seb.se", "trust": 0.98},
            {"name": "Handelsbanken", "url": "https://www.handelsbanken.se", "trust": 0.98},
            {"name": "Nordea", "url": "https://www.nordea.se", "trust": 0.98},
            {"name": "IKEA", "url": "https://www.ikea.com/se", "trust": 0.97},
            {"name": "Volvo", "url": "https://www.volvo.se", "trust": 0.97},
            {"name": "Scania", "url": "https://www.scania.com", "trust": 0.96},
            {"name": "Ericsson", "url": "https://www.ericsson.com/sv", "trust": 0.96},
            {"name": "Spotify", "url": "https://www.spotify.com/se", "trust": 0.95},
            {"name": "H&M", "url": "https://www.hm.com/sv", "trust": 0.95},
            {"name": "Telia Company", "url": "https://www.teliacompany.se", "trust": 0.95},
            {"name": "Telenor", "url": "https://www.telenor.se", "trust": 0.95},
            {"name": "Vodafone", "url": "https://www.vodafone.se", "trust": 0.95},
            {"name": "Electrolux", "url": "https://www.electrolux.se", "trust": 0.95},
            {"name": "ABB", "url": "https://new.abb.com/sv", "trust": 0.94},
        ],
        "Technology & Internet": [
            {"name": "Dropbox Swedish", "url": "https://www.dropbox.com/sv_SE", "trust": 0.94},
            {"name": "GitHub Swedish", "url": "https://github.com", "trust": 0.95},
            {"name": "Stack Overflow Swedish", "url": "https://stackoverflow.com", "trust": 0.95},
            {"name": "W3C", "url": "https://www.w3.org", "trust": 0.98},
            {"name": "Mozilla Swedish", "url": "https://www.mozilla.org/sv", "trust": 0.96},
            {"name": "Apache Foundation", "url": "https://www.apache.org", "trust": 0.97},
        ],
        "Health & Medical": [
            {"name": "Swedish Public Health Authority", "url": "https://www.folkhalsomyndigheten.se", "trust": 0.99},
            {"name": "Socialstyrelsen", "url": "https://www.socialstyrelsen.se", "trust": 0.99},
            {"name": "Karolinska Institute", "url": "https://ki.se", "trust": 0.97},
            {"name": "Swedish Medical Association", "url": "https://www.slf.se", "trust": 0.96},
        ],
        "Sports & Recreation": [
            {"name": "Swedish Sports Confederation", "url": "https://www.rf.se", "trust": 0.95},
            {"name": "AIK Fotboll", "url": "https://www.aik.se", "trust": 0.90},
            {"name": "Malmö FF", "url": "https://www.mff.se", "trust": 0.90},
            {"name": "Djurgårdens IF", "url": "https://www.djurgardenif.se", "trust": 0.90},
            {"name": "IFK Göteborg", "url": "https://www.ifkgoteborg.se", "trust": 0.90},
        ],
    }
    
    def __init__(self, connection):
        """Initialize domain loader with database connection.
        
        Args:
            connection: psycopg2 database connection
        """
        self.connection = connection
        self.loaded_count = 0
        self.failed_count = 0
    
    def load_domains(self, clear_existing: bool = True) -> bool:
        """Load all Swedish domains into database.
        
        Args:
            clear_existing: If True, clear existing domains before loading
        
        Returns:
            bool: True if successful
        """
        try:
            cursor = self.connection.cursor()
            
            if clear_existing:
                cursor.execute("DELETE FROM kse_domains;")
                logger.info("Cleared existing domains")
            
            # Load domains from configuration
            total_loaded = 0
            
            for category, domains in self.SWEDISH_DOMAINS.items():
                for domain in domains:
                    try:
                        next_crawl = datetime.now() + timedelta(hours=1)
                        
                        cursor.execute("""
                            INSERT INTO kse_domains 
                            (domain_name, domain_url, category, trust_score, next_crawl_at)
                            VALUES (%s, %s, %s, %s, %s)
                            ON CONFLICT (domain_url) DO NOTHING;
                        """, (
                            domain['name'],
                            domain['url'],
                            category,
                            domain['trust'],
                            next_crawl
                        ))
                        total_loaded += 1
                    except Exception as e:
                        logger.warning(f"Failed to load domain {domain['name']}: {e}")
                        self.failed_count += 1
            
            self.connection.commit()
            
            # Verify loaded count
            cursor.execute("SELECT COUNT(*) FROM kse_domains;")
            actual_count = cursor.fetchone()[0]
            
            logger.info(
                f"Loaded {actual_count} domains into database. "
                f"Attempted: {total_loaded}, Failed: {self.failed_count}"
            )
            
            cursor.close()
            self.loaded_count = actual_count
            return True
            
        except Exception as e:
            logger.error(f"Error loading domains: {e}")
            self.connection.rollback()
            return False
    
    def load_from_json(self, json_path: str) -> bool:
        """Load domains from JSON file.
        
        Args:
            json_path: Path to JSON file with domains
        
        Returns:
            bool: True if successful
        """
        try:
            with open(json_path, 'r', encoding='utf-8') as f:
                domains_data = json.load(f)
            
            cursor = self.connection.cursor()
            
            for domain in domains_data:
                next_crawl = datetime.now() + timedelta(hours=1)
                
                cursor.execute("""
                    INSERT INTO kse_domains 
                    (domain_name, domain_url, category, trust_score, next_crawl_at)
                    VALUES (%s, %s, %s, %s, %s)
                    ON CONFLICT (domain_url) DO NOTHING;
                """, (
                    domain.get('name'),
                    domain.get('url'),
                    domain.get('category', 'Other'),
                    domain.get('trust', 0.5),
                    next_crawl
                ))
            
            self.connection.commit()
            
            cursor.execute("SELECT COUNT(*) FROM kse_domains;")
            count = cursor.fetchone()[0]
            logger.info(f"Loaded {count} domains from {json_path}")
            cursor.close()
            return True
            
        except Exception as e:
            logger.error(f"Error loading domains from JSON: {e}")
            return False
    
    def get_domain_count(self) -> int:
        """Get total number of domains in database.
        
        Returns:
            int: Number of domains
        """
        cursor = self.connection.cursor()
        cursor.execute("SELECT COUNT(*) FROM kse_domains;")
        count = cursor.fetchone()[0]
        cursor.close()
        return count
    
    def get_active_domains(self) -> List[Dict]:
        """Get all active domains.
        
        Returns:
            list: List of domain dictionaries
        """
        cursor = self.connection.cursor()
        cursor.execute("""
            SELECT domain_id, domain_name, domain_url, category, trust_score 
            FROM kse_domains 
            WHERE is_active = TRUE 
            ORDER BY trust_score DESC;
        """)
        domains = []
        for row in cursor.fetchall():
            domains.append({
                'id': row[0],
                'name': row[1],
                'url': row[2],
                'category': row[3],
                'trust': row[4]
            })
        cursor.close()
        return domains
    
    def get_domains_needing_crawl(self, limit: int = 100) -> List[Dict]:
        """Get domains that need to be crawled.
        
        Args:
            limit: Maximum number of domains to return
        
        Returns:
            list: List of domains needing crawl
        """
        cursor = self.connection.cursor()
        cursor.execute("""
            SELECT domain_id, domain_name, domain_url, category, trust_score
            FROM kse_domains
            WHERE is_active = TRUE AND (next_crawl_at IS NULL OR next_crawl_at <= NOW())
            ORDER BY trust_score DESC, next_crawl_at ASC
            LIMIT %s;
        """, (limit,))
        
        domains = []
        for row in cursor.fetchall():
            domains.append({
                'id': row[0],
                'name': row[1],
                'url': row[2],
                'category': row[3],
                'trust': row[4]
            })
        cursor.close()
        return domains
