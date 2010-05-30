//
//  Database.h
//  TestDB
//
//  Created by Jérôme Laheurte on 12/12/08.
//  Copyright 2008 Jérôme Laheurte. See COPYING for details.
//

#import <Foundation/Foundation.h>

#import "SQLite.h"
#import "CDFile.h"

@interface Database : SQLite
{
	NSNumber *currentFile;
	CDFile *cdCurrentFile;
	NSInteger fileNumber;
}

@property (nonatomic, retain) NSNumber *currentFile;
@property (nonatomic, readonly) NSInteger fileNumber;

@property (nonatomic, retain) CDFile *cdCurrentFile;
@property (nonatomic, readonly) NSInteger cdFileCount;

// This is a Singleton
+ (Database *)connection;
+ (void)close;

@end
