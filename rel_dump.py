import contextlib
import sqlite3


def run():
    dbpath = 'projects.db'
    with contextlib.closing(sqlite3.connect(dbpath)) as conn:
        with conn as cur:
            rows = cur.execute('''
SELECT
    projects_w.project_id,
    projects_w.game_title,
    packages_w.package_id,
    packages_w.name,
    releases_w.release_id,
    releases_w.version,
    files_w.version,
    files_w.filename
FROM projects_w
LEFT OUTER JOIN packages_w
    ON projects_w.project_id = packages_w.project_id
LEFT OUTER JOIN releases_w
    ON packages_w.package_id = releases_w.package_id
LEFT OUTER JOIN files_w
    ON releases_w.release_id = files_w.release_id
WHERE
    packages_w.package_id IS NULL
    OR (
        files_w.filename IS NOT NULL
        AND files_w.url IS NOT NULL
    )
ORDER BY
    projects_w.game_title ASC,
    packages_w.package_id ASC,
    releases_w.version_major DESC,
    releases_w.version_minor DESC,
    releases_w.version_patch DESC,
    releases_w.version_pre DESC NULLS FIRST,
    releases_w.version_build DESC NULLS FIRST,
    files_w.version_major DESC,
    files_w.version_minor DESC,
    files_w.version_patch DESC,
    files_w.version_pre DESC NULLS FIRST,
    files_w.version_build DESC NULLS FIRST,
    files_w.filename ASC
                '''
            )

            proj_id = None
            pkg_id = None
            rel_id = None

            for r in rows:
                if r[0] != proj_id:
                    print('')
                    proj_id = r[0]
                    print(r[1])

                if r[2] != pkg_id:
                    pkg_id = r[2]
                    if pkg_id is not None:
                        print(' ', r[3])

                if r[4] != rel_id:
                    rel_id = r[4]
                    if rel_id is not None:
                        print('   ', r[5])

                if pkg_id is not None and rel_id is not None:
                    print('     ', r[6:])




if __name__ == '__main__':
    run()
