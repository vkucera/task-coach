//
//  SQLite.h
//  iBooks
//
//  Created by Jérôme Laheurte on 10/12/08.
//  Copyright 2008 Jérôme Laheurte. See COPYING for details.
//

#import <Foundation/Foundation.h>
#import <sqlite3.h>

@class Statement;

@interface SQLite : NSObject {
	sqlite3 *pDb;
	BOOL inTransaction;
	NSInteger dbVersion;
}

@property (readonly) BOOL inTransaction;

- initWithFilename:(NSString *)filename;

- (NSString *)errmsg;
- (sqlite3 *)connection;

- (Statement *)statementWithSQL:(NSString *)sql;

- (void)begin;
- (void)commit;
- (void)rollback;

- (NSInteger)lastRowID;

@end
