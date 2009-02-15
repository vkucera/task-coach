//
//  PositionStore.h
//  TaskCoach
//
//  Created by Jérôme Laheurte on 01/02/09.
//  Copyright 2009 __MyCompanyName__. All rights reserved.
//

#import <Foundation/Foundation.h>

@interface Position : NSObject <NSCoding>
{
	NSInteger scrollPosition;
	NSIndexPath *indexPath;
}

@property (nonatomic, readonly) CGPoint scrollPosition;
@property (nonatomic, readonly) NSIndexPath *indexPath;

- initWithController:(UITableViewController *)controller indexPath:(NSIndexPath *)indexPath;

@end

@interface PositionStore : NSObject
{
	NSMutableArray *positions;
	NSInteger current;
}

+ (PositionStore *)instance;

- initWithFile:(NSString *)path;
- (void)save:(NSString *)path;

- (void)push:(UITableViewController *)controller indexPath:(NSIndexPath *)indexPath;
- (void)pop;

- (void)restore:(UIViewController *)controller;

@end
