//
//  Statement.h
//  iBooks
//
//  Created by Jérôme Laheurte on 10/12/08.
//  Copyright 2008 Jérôme Laheurte. See COPYING for details.
//

#import <Foundation/Foundation.h>
#import <sqlite3.h>

@class SQLite;

@interface Statement : NSObject {
	sqlite3_stmt *pReq;
	SQLite *connection;
	
	NSInteger colCount;
	NSMutableArray *colNames;

	id myTarget;
	SEL myAction;
}

- initWithConnection:(SQLite *)cn andSQL:(NSString *)sql;

- (void)bindInteger:(NSInteger)value atIndex:(NSInteger)index;
- (void)bindString:(NSString *)string atIndex:(NSInteger)index;
- (void)bindNullAtIndex:(NSInteger)index;

- (void)exec;
// Returns the number of rows
- (NSInteger)execWithTarget:(id)target action:(SEL)action;

- (void)startWithTarget:(id)target action:(SEL)action;
- (BOOL)next;

@end
