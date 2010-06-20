//
//  PositionStore.h
//  TaskCoach
//
//  Created by Jérôme Laheurte on 01/02/09.
//  Copyright 2009 Jérôme Laheurte. See COPYING for details.
//

#import <Foundation/Foundation.h>

@class PositionStore;
@class Position;

#define TYPE_SUBTASK 0
#define TYPE_DETAILS 1

@protocol RestorableController

- (UITableView *)tableView;
- (void)restorePosition:(Position *)pos store:(PositionStore *)store;

@end

@interface Position : NSObject <NSCoding>
{
	NSInteger _scrollPosition;
	NSIndexPath *indexPath;
	NSInteger type;
	NSString *searchWord;
	NSInteger tab;
}

@property (nonatomic, readonly) CGPoint scrollPosition;
@property (nonatomic, readonly) NSIndexPath *indexPath;
@property (nonatomic, readonly) NSInteger type;
@property (nonatomic, copy) NSString *searchWord;
@property (nonatomic) NSInteger tab;

- initWithController:(id <RestorableController>)controller indexPath:(NSIndexPath *)indexPath type:(NSInteger)type searchWord:(NSString *)searchWord;

@end

@interface PositionStore : NSObject
{
	NSMutableArray *positions;
	NSInteger current;
}

+ (PositionStore *)instance;

- initWithFile:(NSString *)path;
- (void)save:(NSString *)path;

- (void)setTab:(NSInteger)tab;

- (void)setRoot:(id <RestorableController>)controler indexPath:(NSIndexPath *)indexPath type:(NSInteger)type searchWord:(NSString *)searchWord;
- (void)push:(id <RestorableController>)controller indexPath:(NSIndexPath *)indexPath type:(NSInteger)type searchWord:(NSString *)searchWord;
- (void)pop;

- (void)restore:(id <RestorableController>)controller;

@end
