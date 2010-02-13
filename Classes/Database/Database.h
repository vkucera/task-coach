//
//  Database.h
//  TestDB
//
//  Created by Jérôme Laheurte on 12/12/08.
//  Copyright 2008 Jérôme Laheurte. See COPYING for details.
//

#import <Foundation/Foundation.h>

#import "SQLite.h"

@interface Database : SQLite
{
	NSNumber *currentFile;
	NSInteger fileNumber;
}

@property (nonatomic, retain) NSNumber *currentFile;
@property (nonatomic, readonly) NSInteger fileNumber;

// This is a Singleton
+ (Database *)connection;
+ (void)close;

@end
