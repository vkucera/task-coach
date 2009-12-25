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
}

@property (nonatomic, retain) NSNumber *currentFile;

// This is a Singleton
+ (Database *)connection;
+ (void)close;

@end
