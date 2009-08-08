//
//  TaskCell.h
//  TaskCoach
//
//  Created by Jérôme Laheurte on 17/01/09.
//  Copyright 2009 Jérôme Laheurte. See COPYING for details.
//

#import <UIKit/UIKit.h>

@class Task;
@class CheckView;

@interface TaskCell : UITableViewCell
{
	NSInteger taskId;

	CheckView *leftImage;
	UILabel *titleLabel;
	
	id target;
	SEL action;
	
	BOOL isTapping;
}

@property (nonatomic, readonly) NSInteger taskId;
@property (nonatomic, retain) IBOutlet CheckView *leftImage;
@property (nonatomic, retain) IBOutlet UILabel *titleLabel;

- (void)setTask:(Task *)task target:(id)target action:(SEL)action;

@end
